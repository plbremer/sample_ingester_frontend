

import dash
from dash import dcc, html,callback
from dash.dependencies import Input, Output, State

import plotly.express as px
import dash_bootstrap_components as dbc

from dash.exceptions import PreventUpdate

import pandas as pd

import xlsxwriter

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
        'tissue':['species','organ','disease','sex','height','height_unit','weight','weight_unit','age','age_unit','other_inclusion_criteria','other_exclusion_criteria'],
        'fluid':['species','organ','disease','sex','height','height_unit','mass','mass_unit','age','age_unit','other_inclusion_criteria','other_exclusion_criteria'],
        'cells':['species','cell_line','cell_count','other_inclusion_criteria','other_exclusion_criteria'],
        'raw_material':['material','mass','mass_unit','volume','volume_unit','other_inclusion_criteria','other_exclusion_criteria'],
        'genetic':['gene'],
        'longitudinal':['zero_time_event','time','time_unit'],
        'effect':['drug_name','drug_dose_volume_or_mass','drug_dose_unit','diet','exercise'],
        #'general':[,'other_inclusion_criteria','other_exclusion_criteria']
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
                dbc.Col(width=3),
                dbc.Col(
                    children=[
                        html.H3('Sample Types'),
                        html.Br(),
                        dbc.Checklist(
                            options=[
                                {"label": "Tissue, Organs (lung, heart, etc.)", "value": 'tissue'},
                                {"label": "Biofluids (plasma, urine, etc.)", "value": 'fluid'},
                                {"label": "Cells", "value": 'cells'},
                                {"label": "Raw Material (soil, water, gas, etc.)", "value": 'raw_material'},
                            ],
                            #value=[1],
                            id="sample_checklist",
                        ),
                    ],
                    width=4
                ),
                dbc.Col(
                    children=[
                        html.H3('Study Types'),
                        html.Br(),
                        dbc.Checklist(
                            options=[
                                {"label": "Genetic", "value": 'genetic'},
                                {"label": "Time Series (Longitudinal)", "value": 'longitudinal'},
                                {"label": "Intervention/Effect", "value": 'effect'},
                            ],
                            #value=[1],
                            id="study_checklist",
                        ),
                    ],
                    width=4
                ),
                dbc.Col(width=1)
            ]
        ),
        html.Br(),
        html.Br(),
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
        html.Br(),
        html.Br(),
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

    output_stream=io.BytesIO()
    temp_writer=pd.ExcelWriter(output_stream,engine='xlsxwriter')

    empty_df=pd.DataFrame()
    empty_df.to_excel(temp_writer,sheet_name='title_page',index=False)
    temp_dataframe.to_excel(temp_writer,sheet_name='sample_sheet',index=False)

    #https://xlsxwriter.readthedocs.io/working_with_pandas.html
    #https://community.plotly.com/t/generate-multiple-tabs-in-excel-file-with-dcc-send-data-frame/53460/7
    workbook=temp_writer.book
    worksheet=temp_writer.sheets['sample_sheet']
    worksheet.autofit()

    worksheet=temp_writer.sheets['title_page']
    worksheet.hide_gridlines()
    worksheet.write('B2','Hello. Please write one sample per row.')
    worksheet.write('B3','Please leave unused metadata blank.')

    temp_writer.save()
    temp_data=output_stream.getvalue()
    #output_excel

    return [
        dcc.send_bytes(temp_data,"binbase_sample_ingestion_form.xlsx")
    ]

    # return [
    #     dcc.send_data_frame(
    #         temp_dataframe.to_excel, "binbase_sample_ingestion_form.xlsx", sheet_name="sample_information", index=False
    #     )
    # ]


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
        #this state component is not necessary
        State(component_id="main_store",component_property="data"),
    ],
    prevent_initial_call=True
)
def upload_form(
    upload_form_contents,
    upload_form_filename,
    upload_form_last_modified,
    main_store_data
):
    if upload_form_contents==None:
        raise PreventUpdate
    
    '''
    need to have things like prevent update if its not an excel file
    '''
    print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~`')
    print(main_store_data)
    #print(upload_form_contents)


    content_type, content_string = upload_form_contents.split(',')
    # decoded = base64.b64decode(content_string)
    # df = pd.read_excel(io.BytesIO(decoded))

    decoded=base64.b64decode(content_string)

    temp_dataframe=pd.read_excel(
        io.BytesIO(decoded),
        #index_col=False
    )

    print(temp_dataframe)

    temp_dataframe_as_json=temp_dataframe.to_json(orient='records')

    print(temp_dataframe_as_json)
    displayed_name=[html.H5(upload_form_filename,className='text-center')]
    return [displayed_name,temp_dataframe_as_json]