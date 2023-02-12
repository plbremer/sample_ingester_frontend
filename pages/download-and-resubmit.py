

import dash
from dash import dcc, html,callback
from dash.dependencies import Input, Output, State

import plotly.express as px
import dash_bootstrap_components as dbc

from dash.exceptions import PreventUpdate

import pandas as pd

import base64
import io

dash.register_page(__name__, path='/download-and-resubmit')


def generate_form_headers(selected_sample_archetypes):
    '''
    a more sophisticated approach needs to be implemented.
    should probably read from a support file.
    need to make it so that properties dont appear multiple times
    '''
    form_header_dict={
        'living_tissue':['species','organ','sex','diet','height','height_unit','weight','weight_unit','age','age_unit'],
        'living_cells':['species','cell_line','cell_count'],
        'raw_material':['medium','mass','mass_unit','volume','volume_unit'],
        'knockout':['gene'],
        'time':['zero_time_event','time','time_unit'],
        'drug':['drug_name','drug_dose','drug_dose_unit'],
        'general':['inclusion_criteria','exclusion_criteria']
    }

    total_headers=[]
    for temp_header in selected_sample_archetypes:
        for temp_element in form_header_dict[temp_header]:
            if temp_element not in total_headers:
                total_headers.append(temp_element)
    
    return total_headers



layout = html.Div(
    children=[
        dcc.Download(id="download_form"),
        html.Br(),
        html.Br(),
        dbc.Row(
            children=[
                dbc.Col(width=1),
                dbc.Col(
                    children=[
                        html.H3('Sample Descriptors'),
                        dbc.Checklist(
                            options=[
                                {"label": "Living Tissue, Organs (plasma, lung, etc.)", "value": 'living_tissue'},
                                {"label": "Living Cells (pure cells?)", "value": 'living_cells'},
                                {"label": "Raw Material (soil, water, etc.)", "value": 'raw_material'},
                            ],
                            #value=[1],
                            id="sample_checklist",
                        ),
                    ],
                    width=4
                ),
                dbc.Col(
                    children=[
                        html.H3('Study Descriptors'),
                        dbc.Checklist(
                            options=[
                                {"label": "Gene Knockout", "value": 'knockout'},
                                {"label": "Time Series", "value": 'time'},
                                {"label": "Drug Administration", "value": 'drug'},
                            ],
                            #value=[1],
                            id="study_checklist",
                        ),
                    ],
                    width=4
                ),
                dbc.Col(width=2)
            ]
        ),
        html.Br(),
        html.Br(),
        dbc.Row(
            children=[
                dbc.Col(width=5),
                dbc.Col(
                    children=[
                        html.Div(
                            dbc.Button(
                                'Download Form',
                                id='button_form',
                            ),
                            className="d-grid gap-2 col-6 mx-auto",
                        ),
                    ],
                    width=2
                ),
                dbc.Col(width=5)
            ]
        ),
        html.Br(),
        html.Br(),
        dbc.Row(
            children=[
                dbc.Col(width=5),
                dbc.Col(
                    children=[
                        dcc.Upload(
                            id='upload_form',
                            children=html.Div([
                                'Drag and Drop or ',
                                html.A('Select Files')
                            ]),
                            style={
                                'width': '100%',
                                'height': '60px',
                                'lineHeight': '60px',
                                'borderWidth': '1px',
                                'borderStyle': 'dashed',
                                'borderRadius': '5px',
                                'textAlign': 'center',
                                'margin': '10px'
                            },
                        ),
                    ],
                    width=2
                ),
                dbc.Col(width=5)
            ]
        ),
        html.Br(),


        dbc.Row(
            children=[
                dbc.Col(width=5),
                dbc.Col(
                    children=[
                        html.Div(id='div_filename')
                    ],
                    width=2
                ),
                dbc.Col(width=5)
            ]
        ),









        dbc.Row(
            children=[
                dbc.Col(width=5),
                dbc.Col(
                    children=[
                        
                        dcc.Link(
                            children=[                        
                                html.Div(
                                    dbc.Button(
                                        'Process Form',
                                        id='button_form',
                                    ),
                                    className="d-grid gap-2 col-6 mx-auto",
                                ),
                            ],
                            href='/curate-and-download',
                            #refresh=True
                        )

                    ],
                    width=2
                ),
                dbc.Col(width=5)
            ]
        ),









    ],
)

@callback(
    [
        Output(component_id="download_form", component_property="data"),
    ],
    [
        Input(component_id='button_form', component_property='n_clicks'),
    ],
    [
        State(component_id='sample_checklist', component_property='value'),
        State(component_id='study_checklist',component_property='value'),
    ],
)
def generate_form(button_form_n_clicks,sample_checklist_options,study_checklist_options):
    '''
    '''
    if sample_checklist_options==None and study_checklist_options==None:
        raise PreventUpdate
    
    print(sample_checklist_options)
    if sample_checklist_options==None:
        sample_checklist_options=[]
    if study_checklist_options==None:
        study_checklist_options=[]
    total_headers=generate_form_headers(sample_checklist_options+study_checklist_options)
    print(total_headers)

    temp_dataframe=pd.DataFrame.from_dict(
        {element:[] for element in total_headers}
    )
    print(temp_dataframe)

    return [
        dcc.send_data_frame(
            temp_dataframe.to_excel, "binbase_sample_ingestion_form.xlsx", sheet_name="sample_information", index=False
        )
    ]


@callback(
    [
        #Output(component_id="here_is_where_we_put_the curation_interface", component_property="children"),
        Output(component_id="div_filename", component_property="children"),
        Output(component_id="main_store",component_property="data")
    ],
    [
        Input(component_id="upload_form", component_property="contents"),
    ],
    [
        State(component_id="upload_form", component_property="filename"),
        State(component_id="upload_form", component_property="last_modified"),
        State(component_id="main_store",component_property="data"),
    ],
    prevent_initial_call=True
)
def upload_form(
    upload_form_contents,
    upload_form_filename,
    upload_form_last_modified,
    TEMP
):
    if upload_form_contents==None:
        raise PreventUpdate
    
    '''
    need to have things like prevent update if its not an excel file
    '''
    print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~`')
    print(TEMP)
    
    
    print(upload_form_contents)

    # decoded = base64.b64decode(content_string)
    # df = pd.read_excel(io.BytesIO(decoded))

    content_type, content_string = upload_form_contents.split(',')
    # decoded = base64.b64decode(content_string)
    # df = pd.read_excel(io.BytesIO(decoded))

    decoded=base64.b64decode(content_string)

    temp_dataframe=pd.read_excel(
        io.BytesIO(decoded),
        #index_col=False
    )

    print(temp_dataframe)

    temp_dataframe_as_json=temp_dataframe.to_records(index=False)

    print(temp_dataframe_as_json)
    displayed_name=[html.H5(upload_form_filename)]
    return [displayed_name,temp_dataframe_as_json]