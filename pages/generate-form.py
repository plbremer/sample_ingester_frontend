
import dash
from dash import dcc, html,dash_table,callback, ctx,MATCH,ALL
import plotly.express as px
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import dash_mantine_components as dmc

import json
import numpy as np

NUM_STEPS=3


#def read_archetype_to_header_dict():
with open('assets/form_header_dict_basics.json','r') as f:
    FORM_HEADER_DICT=json.load(f)
with open('assets/extra_columns.json','r') as f:
    EXTRA_COLUMNS=json.load(f)
#read_archetype_to_header_dict()


def generate_form_headers(selected_archetypes):
    '''
    from the selected archetypes ('tissue', 'genetic', etc.)
    create the total set of metadata headers. order matters 
    '''
    total_headers=[]
    for temp_header in selected_archetypes:
        for temp_element in FORM_HEADER_DICT[temp_header]:
            if temp_element not in total_headers:
                total_headers.append(temp_element)
    
    return total_headers

def generate_extra_headers(selected_types):
    total_headers=[]
    for temp_header in selected_types:
        total_headers+=EXTRA_COLUMNS[temp_header]

    return total_headers


dash.register_page(__name__, path='/generate-form')


layout = html.Div(
    children=[
        dcc.Download(id="download_form"),
        html.Br(),
        html.Br(),

        html.Div(
            id='Div_metadata_datatable',
            children=[
                dash_table.DataTable(
                    id='dt_for_preview',
                    columns=None,
                    data=None,
                )
            ]
        ),

        # dbc.Row(
        #     children=[
        #         dbc.Col(width=3),
        #         dbc.Col(
        #             children=[
        #                 html.H6('hi')
        #             ]
        #         )
        #     ]
        # ),
        html.Br(),
        html.Br(),
        html.Br(),
        html.Br(),

        html.Div(
            children=[
                dmc.Stepper(
                    id="stepper_generate_form",
                    active=0,
                    breakpoint="sm",
                    children=[
                        dmc.StepperStep(
                            label="First step",
                            description="Choose Archetypes",
                            children=[
                                dbc.Row(
                                    children=[
                                        dbc.Col(width=3),
                                        dbc.Col(
                                            children=[
                                                html.H3('Sample Types'),
                                                html.Br(),
                                                dbc.Checklist(
                                                    options=[
                                                        {"label": "Tissue (lung, heart, etc.)", "value": 'tissue'},
                                                        {"label": "Biofluids (plasma, urine, etc.)", "value": 'fluid'},
                                                        {"label": "Cells (culture, organoid, etc.)", "value": 'cells'},
                                                        {"label": "Raw Material (soil, water, gas, etc.)", "value": 'raw_material'},
                                                    ],
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
                                                        {"label": "Genetic (knockout, CRISPR, MIR, etc.)", "value": 'genetic'},
                                                        {"label": "Time Series (longitudinal)", "value": 'longitudinal'},
                                                        {"label": "Intervention (drug, diet, exercise, etc.)", "value": 'intervention'},
                                                        {"label": "Effect (disease, etc.)", "value": 'effect'},
                                                    ],
                                                    id="study_checklist",
                                                ),
                                            ],
                                            width=4
                                        ),
                                        dbc.Col(width=1)
                                    ]
                                )
                            ]
                        ),
                        dmc.StepperStep(
                            label="Second step",
                            description="Extra Specifications",
                            children=[
                                dbc.Row(
                                    children=[
                                        dbc.Col(width=3),
                                        dbc.Col(
                                            children=[
                                                html.H3('Sample Types'),
                                                html.Br(),
                                                dbc.Checklist(
                                                    options=[
                                                        {"label":temp_key, "value":temp_key} for temp_key in EXTRA_COLUMNS
                                                    ],
                                                    id="extra_checklist",
                                                ),
                                            ],
                                            width=4
                                        ),
                                        dbc.Col(
                                            children=[
                                                html.H3('Number of Samples'),
                                                html.Br(),
                                                dmc.NumberInput(
                                                    id='sample_count_input',
                                                    label="Number of Samples",
                                                    description="Integer from 1 to infinity",
                                                    value=1,
                                                    min=1,
                                                    step=1,
                                                    style={"width": 250},
                                                ),
                                            ],
                                            width=4
                                        ),
                                        dbc.Col(width=1)
                                    ]
                                )
                            ]
                            
                            
                            
                        ),
                        
                        dmc.StepperStep(
                            label="third step",
                            description="asdfgasdfg",
                            children=[


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











                            ]
                        ),
                        dmc.StepperCompleted(
                            # label='some_label',
                            # description='some description',



                            
                            children=[
                                dbc.Row(
                                    children=[
                                        dbc.Col(width=5),
                                        dbc.Col(
                                            children=[
                                                html.Div(
                                                    dbc.Button(
                                                        dbc.NavLink('Go home', href='/',style = {'color': 'white','font-weight':'bold'},className='navlink-parker'),#,className='nav-link'))
                                                    ),
                                                    className="d-grid gap-2 col-6 mx-auto",
                                                ),
                                            ],
                                            width=2
                                        ),
                                        dbc.Col(width=5)
                                    ]
                                ),

                            ]
                        ),
                    ],
                ),
                dmc.Group(
                    position="center",
                    mt="xl",
                    children=[
                        dbc.Button("Back", id="stepper_generate_form_back"),# variant="default"),
                        dbc.Button("Next step", id="stepper_generate_form_next")
                    ],
                ),
            ]
        )


    ]
)



@callback(
    [
        Output(component_id="stepper_generate_form", component_property="active"),
        Output(component_id="stepper_generate_form", component_property="children")
    ],
    [
        Input(component_id='stepper_generate_form_back', component_property="n_clicks"),
        Input(component_id='stepper_generate_form_next', component_property="n_clicks")
    ],
    [
        State(component_id="stepper_generate_form", component_property="active"),
        State(component_id="stepper_generate_form", component_property="children")
    ],
    prevent_initial_call=True
)
def update(stepper_generate_form_back_n_clicks, stepper_generate_form_next_n_clicks, current,my_children):
    # print('-------')
    # print(ctx.triggered_id)
    print(current)
    # button_id = ctx.triggered_id
    # step = current if current is not None else active
    # if button_id == "back-basic-usage":
    #     step = step - 1 if step > min_step else step
    # else:
    #     step = step + 1 if step < max_step else step
    if ctx.triggered_id=="stepper_generate_form_back" and current>0:
        current-=1
    elif ctx.triggered_id=="stepper_generate_form_next" and current<NUM_STEPS:
        current+=1        
    # print(step)
    
    output_children=my_children
    output_children[current]=my_children[current]


    # #output_children=my_children
    # current_time=time()
    # if current<3:
    #     my_children[current]=dmc.StepperStep(
    #                     label='this_should_be_dynamic',
    #                     description="this_should_be_tynamic",
    #                     children=dmc.Text(
    #                         f"the previous time was {current_time}", align="center"
    #                     ),
    #                 )
    # else:
    #     my_children[current]=dmc.StepperCompleted(
    #                 children=dmc.Text(
    #                     "Completed, click back button to get to previous step",
    #                     align="center",
    #                 )
    #             ),      

    # print('about to output')
    return [current,my_children]




        # html.Div(
        #     id='Div_metadata_datatable',
        #     children=[
        #         dash_table.DataTable(
        #             id='dt_for_preview',
        #             columns=None,
        #             data=None,
        #         )
        #     ]
        # ),



@callback(
    [
        Output(component_id="Div_metadata_datatable", component_property="children"),
    ],
    [
        # Input(component_id='stepper_generate_form_back', component_property="n_clicks"),
        # Input(component_id='stepper_generate_form_next', component_property="n_clicks")
        Input(component_id='sample_checklist', component_property='value'),
        Input(component_id='study_checklist',component_property='value'),
        Input(component_id="extra_checklist",component_property='value'),
        Input(component_id="sample_count_input",component_property='value'),
    ],
    [
        State(component_id='sample_checklist', component_property='value'),
        State(component_id='study_checklist',component_property='value'),
        State(component_id="extra_checklist",component_property='value'),
        State(component_id="sample_count_input",component_property='value'),
    ],
    prevent_initial_call=True
)
def update(a,b,c,d,sample_checklist_values,study_checklist_values,extra_checklist_values,sample_count_input_value):

    #### This should be something different. should probably just generate an empty DT ####
    if sample_checklist_values==None and study_checklist_values==None:
        raise PreventUpdate

    if sample_checklist_values==None:
        sample_checklist_values=[]
    if study_checklist_values==None:
        study_checklist_values=[]

    if extra_checklist_values==None:
        extra_checklist_values=[]


    archetype_headers=generate_form_headers(sample_checklist_values+study_checklist_values)
    extra_headers=generate_extra_headers(extra_checklist_values)
    
    total_headers=archetype_headers+extra_headers
    
    total_columns=[
        {'name':temp_element, 'id':temp_element} for temp_element in total_headers
    ]

    #total_data=list()
    #total_data.append(
    total_data=[
        {
            temp_col['id']:'download this table' for temp_col in total_columns
        }
        for temp_row in range(sample_count_input_value)
    ]

    #print(total_headers)

    output_children=[
        dash_table.DataTable(
            id='dt_for_preview',
            columns=total_columns,
            data=total_data,
            style_cell={
                'fontSize': 17,
                'padding': '8px',
                'textAlign': 'center'
            },
            style_header={
                'font-family': 'arial',
                'fontSize': 15,
                'fontWeight': 'bold',
                'textAlign': 'center'
            },
            style_data={
                'textAlign': 'center',
                'fontWeight': 'bold',
                'font-family': 'Roboto',
                'fontSize': 15,
            },
            style_table={
                'overflowX': 'scroll'
            }
        )
    ]

    return [output_children]


@callback(
    [
        Output(component_id="download_form", component_property="data"),
    ],
    [
        Input(component_id='button_form', component_property='n_clicks'),
    ],
    # [
    #     State(component_id='sample_checklist', component_property='value'),
    #     State(component_id='study_checklist',component_property='value'),
    # ],
    [
        #State(component_id="column_store", component_property="data"),
        State(component_id="dt_for_preview",component_property="columns")
    ],
)
# def generate_form(button_form_n_clicks,sample_checklist_options,study_checklist_options):
def generate_form(button_form_n_clicks,dt_for_preview_columns):
    '''
    creates the form that is downloaded by users
    '''
    print('+++++++++++++++++++++++++++')
    print(ctx.triggered_id)
    #a potential improvement would be to generate a visible error if nothing is checked
    if dt_for_preview_columns==None:# and study_checklist_options==None:
        raise PreventUpdate
    
    # if sample_checklist_options==None:
    #     sample_checklist_options=[]
    # if study_checklist_options==None:
    #     study_checklist_options=[]
    
    #multipele archetypes can have the same headers (eg tissue, cells both have species)
    #we want a non-repeating, ordered list of those headers
    # total_headers=generate_form_headers(sample_checklist_options+study_checklist_options)

    #get the dicts that define the colors for the excel file
    # group_to_header_dict,group_to_archetype_dict=generate_header_colors(sample_checklist_options+study_checklist_options,total_headers)

    #need to rearrange columns to match group order
    # column_order_list=sum(group_to_header_dict.values(),[])

    #empty df for excel file
    temp_dataframe=pd.DataFrame.from_dict(
        {element['id']:[] for element in dt_for_preview_columns}
    )

    #we write to bytes because it is much more versatile
    output_stream=io.BytesIO()
    temp_writer=pd.ExcelWriter(output_stream,engine='xlsxwriter')
    #temp_writer=pd.ExcelWriter(output_stream,engine='openpyxl')

    empty_df=pd.DataFrame()
    empty_df.to_excel(temp_writer,sheet_name='title_page',index=False)
    temp_dataframe.to_excel(temp_writer,sheet_name='sample_sheet',index=False)#,startrow=1)

    #https://xlsxwriter.readthedocs.io/working_with_pandas.html
    #https://community.plotly.com/t/generate-multiple-tabs-in-excel-file-with-dcc-send-data-frame/53460/7
    workbook=temp_writer.book
    worksheet=temp_writer.sheets['sample_sheet']

    #for each group in group_to_header_dict,group_to_archetype_dict
    #ascertain the number of involved columns in the group
    #ascertain the number of already seen columns
    #merge ((number of involved columns) offset by (number of already seen columns))
    #write text and color ((number of involved columns) offset by (number of already seen columns))
    #for each group, make a format
    #write and color the curation sheet
    
    workbook, worksheet=update_excel_sheet_sample_formatting(workbook,worksheet,temp_dataframe)#,group_to_header_dict,group_to_archetype_dict)
    workbook, worksheet=fill_title_sheet(temp_writer,workbook,worksheet)

    temp_writer.save()
    temp_data=output_stream.getvalue()

    return [
        dcc.send_bytes(temp_data,"binbase_sample_ingestion_form.xlsx")
    ]