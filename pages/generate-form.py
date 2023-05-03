
from random import sample
import dash
from dash import dcc, html,dash_table,callback, ctx,MATCH,ALL
import plotly.express as px
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import dash_mantine_components as dmc

import numpy as np
import pandas as pd
from xlsxwriter.utility import xl_rowcol_to_cell
import json
import base64
import io
from pprint import pprint
import requests


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
    # total_headers=[]
    # for temp_grouping in EXTRA_COLUMNS:
    #     for temp_type in EXTRA_COLUMNS[temp_grouping]:
    #         if temp_type in selected_types:
    #             total_headers+=EXTRA_COLUMNS[temp_grouping][temp_type]
    # return total_headers

dash.register_page(__name__, path='/generate-form')

# extra_column_cols=list()
# for temp_type in EXTRA_COLUMNS:
#     extra_column_cols.append(
#         dbc.Col(
#             children=[
#                 html.H3(temp_type),
#                 html.Br(),
#                 dbc.Checklist(
#                     options=[
#                         {"label":temp_key, "value":temp_key} for temp_key in EXTRA_COLUMNS[temp_type]
#                     ],
#                     id="extra_checklist",
#                 ), 
#             ],
#             width=2
#         )
#     )

def generate_step_1_error_checker(sample_checklist_value):
    print('-----------')
    print(sample_checklist_value)
    if sample_checklist_value==None:
        return 'Must select at least 1 sample type.'
    if len(sample_checklist_value)==0:
        return 'Must select at least 1 sample type.'
    else:
        return False


layout = dmc.MantineProvider(
    theme={
        # "components":{
        #     "Button":{
        #         "styles":{
        #             "color":"green"
        #         }
        #     }
        # }
        "colors":{
            "darkBlue":[
                "#617285",
                "#54677D",
                "#485D77",
                "#3C5471",
                "#304C6D",
                "#25456A",
                "#1A3E68",
                "#1E3857",
                "#203349",
                "#212E3E",
                "#202A35",
                "#1F262E",
                "#1D2228"
            ]
        }
    },
    children=[



html.Div(
    children=[
        
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
        html.Br(),
        html.Br(),
        # html.Br(),
        # html.Br(),
        html.Div(
            children=[
                dbc.Row(
                    children=[
                        dbc.Col(width=1),
                        dbc.Col(
                            children=[
        
                                dmc.Stepper(
                                    id="stepper_generate_form",
                                    active=0,
                                    color='darkBlue',
                                    breakpoint="sm",
                                    children=[
                                        dmc.StepperStep(
                                            id='generate_step_1',
                                            label="First step",
                                            description="Choose Sample Types",
                                            children=[
                                                html.Br(),
                                                dbc.Row(
                                                    html.Div(
                                                        id='generate_step_1_error_div',
                                                        children=[]
                                                    )
                                                ),
                                                dbc.Row(
                                                    children=[
                                                        dbc.Col(width=4),
                                                        dbc.Col(
                                                            html.Div(
                                                            
                                                                children=[
                                                                    html.H3('Sample Types'),
                                                                    # html.Br(),
                                                                    # dbc.Checklist(
                                                                    #     options=[
                                                                    #         {"label": "Tissue (lung, heart, etc.)", "value": 'tissue'},
                                                                    #         {"label": "Biofluids (plasma, urine, etc.)", "value": 'fluid'},
                                                                    #         {"label": "Cells (culture, organoid, etc.)", "value": 'cells'},
                                                                    #         {"label": "Raw Material (soil, water, gas, etc.)", "value": 'raw_material'},
                                                                    #     ],
                                                                    #     id="sample_checklist",
                                                                    # ),
                                                                ],
                                                                className="d-flex justify-content-center align-items-center"
                                                            ),
                                                            width=4
                                                        ),
                                                        # dbc.Col(
                                                        #     children=[
                                                        #         html.H3('Study Types'),
                                                        #         html.Br(),
                                                        #         # dbc.Checklist(
                                                        #         #     options=[
                                                        #         #         {"label": "Genetic (knockout, CRISPR, MIR, etc.)", "value": 'genetic'},
                                                        #         #         {"label": "Time Series (longitudinal)", "value": 'longitudinal'},
                                                        #         #         {"label": "Intervention (drug, diet, exercise, etc.)", "value": 'intervention'},
                                                        #         #         {"label": "Effect (disease, etc.)", "value": 'effect'},
                                                        #         #     ],
                                                        #         #     id="study_checklist",
                                                        #         # ),
                                                        #     ],
                                                        #     width=4
                                                        # ),
                                                        dbc.Col(width=4)
                                                    ]
                                                ),


                                                dbc.Row(
                                                    children=[
                                                        dbc.Col(width=4),
                                                        dbc.Col(
                                                            html.Div(
                                                            
                                                                children=[
                                                                    # html.H3('Sample Types'),
                                                                    html.Br(),
                                                                    dbc.Checklist(
                                                                        options=[
                                                                            {"label": "Tissue (lung, heart, etc.)", "value": 'tissue'},
                                                                            {"label": "Biofluids (plasma, urine, etc.)", "value": 'fluid'},
                                                                            {"label": "Cells (culture, organoid, etc.)", "value": 'cells'},
                                                                            {"label": "Raw Material (soil, water, gas, etc.)", "value": 'raw_material'},
                                                                        ],
                                                                        id="sample_checklist",
                                                                        input_checked_style={
                                                                            'backgroundColor':'#1A3E68',
                                                                            'borderColor':'#1A3E68'
                                                                        }
                                                                    ),
                                                                ],
                                                                className="d-flex justify-content-center align-items-center"
                                                            ),
                                                            width=4
                                                        ),
                                                        # dbc.Col(
                                                        #     children=[
                                                        #         html.H3('Study Types'),
                                                        #         html.Br(),
                                                        #         # dbc.Checklist(
                                                        #         #     options=[
                                                        #         #         {"label": "Genetic (knockout, CRISPR, MIR, etc.)", "value": 'genetic'},
                                                        #         #         {"label": "Time Series (longitudinal)", "value": 'longitudinal'},
                                                        #         #         {"label": "Intervention (drug, diet, exercise, etc.)", "value": 'intervention'},
                                                        #         #         {"label": "Effect (disease, etc.)", "value": 'effect'},
                                                        #         #     ],
                                                        #         #     id="study_checklist",
                                                        #         # ),
                                                        #     ],
                                                        #     width=4
                                                        # ),
                                                        dbc.Col(width=4)
                                                    ]
                                                )
                                            ]
                                        ),
                                        dmc.StepperStep(
                                            label="Second step",
                                            description="Add Extra Columns/Rows",
                                            # children=[
                                            #     dbc.Row(
                                            #         children=[
                                            #             dbc.Col(width=1),
                                            #             dbc.Col(
                                            #                 children=[
                                            #                     html.H3('Additional Metadata'),
                                            #                     html.Br(),
                                            #                     # dbc.Checklist(
                                            #                     #     options=[
                                            #                     #         {"label":temp_key, "value":temp_key} for temp_key in EXTRA_COLUMNS
                                            #                     #     ],
                                            #                     #     id="extra_checklist",
                                            #                     # ),
                                            #                 ],
                                            #                 width=3
                                            #             ),
                                            #             dbc.Col(
                                            #                 children=[
                                            #                     html.H3('Number of Samples'),
                                            #                     html.Br(),
                                            #                     dmc.NumberInput(
                                            #                         id='sample_count_input',
                                            #                         label="Number of Samples",
                                            #                         description="Integer from 1 to infinity",
                                            #                         value=1,
                                            #                         min=1,
                                            #                         step=1,
                                            #                         style={"width": 250},
                                            #                     ),
                                            #                 ],
                                            #                 width=3
                                            #             ),
                                            #             dbc.Col(width=4)
                                            #         ]
                                            #     ),
                                            #     html.Br(),
                                            #     # dbc.Row(
                                            #     #     children=extra_column_cols
                                            #     # )
                                            # ] 
                                            children=[
                                                html.Br(),
                                                dbc.Row(
                                                    children=[
                                                        dbc.Col(width=2),
                                                        dbc.Col(
                                                            children=[
                                                                dbc.Row(
                                                                    children=[
                                                                        html.H3("Sample Dimensions"),
                                                                        dbc.Checklist(
                                                                            options=[
                                                                                {"label": "Sample Mass", "value": 'mass'},
                                                                                {"label": "Sample Volume", "value": 'volume'},
                                                                            ],
                                                                            id="dimension_checklist",
                                                                            input_checked_style={
                                                                                'backgroundColor':'#1A3E68',
                                                                                'borderColor':'#1A3E68'
                                                                            }
                                                                        ),
                                                                    ]
                                                                ),
                                                                html.Br(),
                                                                dbc.Row(
                                                                    children=[
                                                                        html.H3("Sample Extras"),
                                                                        dbc.Checklist(
                                                                            options=[
                                                                                {"label": "Sex", "value": 'sex'},
                                                                                {"label": "Height", "value": 'height'},
                                                                                {"label": "Weight", "value": 'weight'},
                                                                                {"label": "Age", "value": 'age'},
                                                                                {"label": "Ethnicity", "value": 'ethnicity'},
                                                                                {"label": "Geographical Origin", "value": 'geographicalOrigin'},
                                                                                {"label": "Strain", "value": 'strain'},                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           
                                                                            ],
                                                                            id="extras_checklist",
                                                                            input_checked_style={
                                                                                'backgroundColor':'#1A3E68',
                                                                                'borderColor':'#1A3E68'
                                                                            }
                                                                        ),
                                                                    ]
                                                                ),                                                                
                                                            ],
                                                            width=3
                                                        ),
                                                        dbc.Col(
                                                            children=[
                                                                dbc.Row(
                                                                    children=[
                                                                        html.H3("Study Factors"),
                                                                        dbc.Checklist(
                                                                            options=[
                                                                                {"label": "Drug", "value": 'drug'},
                                                                                {"label": "Genotype", "value": 'genotype'},
                                                                                {"label": "Disease", "value": 'disease'},
                                                                                {"label": "Diet", "value": 'diet'},
                                                                                {"label": "Exercise", "value": 'exercise'},                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         
                                                                            ],
                                                                            id="factors_checklist",
                                                                            input_checked_style={
                                                                                'backgroundColor':'#1A3E68',
                                                                                'borderColor':'#1A3E68'
                                                                            }
                                                                        ),
                                                                    ]
                                                                ),  
                                                                html.Br(),
                                                                dbc.Row(
                                                                    children=[
                                                                        html.H3("Time Series"),
                                                                        dbc.Checklist(
                                                                            options=[
                                                                                {"label": "Time Series/Longitudinal Information", "value": 'longitudinal'},                                                                                                                                                                                                                                                                                                                                                                                                      
                                                                            ],
                                                                            id="longitudinal_checklist",
                                                                            input_checked_style={
                                                                                'backgroundColor':'#1A3E68',
                                                                                'borderColor':'#1A3E68'
                                                                            }
                                                                        ),
                                                                    ]
                                                                ),
                                                                html.Br(),
                                                                dbc.Row(
                                                                    children=[
                                                                        html.H3("Other"),
                                                                        dbc.Checklist(
                                                                            options=[
                                                                                {"label": "Other Inclusion Factors", "value": 'inclusion'},
                                                                                {"label": "Other Exclusion Factors", "value": 'exclusion'},
                                                                                {"label": "Comment", "value": 'comment'},                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        
                                                                            ],
                                                                            id="other_checklist",
                                                                            input_checked_style={
                                                                                'backgroundColor':'#1A3E68',
                                                                                'borderColor':'#1A3E68'
                                                                            }
                                                                        ),
                                                                    ]
                                                                ),  
                                                            ],
                                                            width=3
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
                                                            width=3
                                                        ),
                                                    ]
                                                )
                                            ]
                                            
                                        ),
                                        dmc.StepperStep(
                                            label="Third step",
                                            description="Download form",
                                            children=[
                                                dcc.Download(id="download_form"),
                                                html.Br(),
                                                html.Br(),
                                                dbc.Row(
                                                    children=[
                                                        dbc.Col(width=4),
                                                        dbc.Col(
                                                            children=[
                                                                html.Div(
                                                                    children=[
                                                                        html.H6('Download and complete sample metadata form.'),
                                                                        #html.H6('Reupload '),
                                                                        html.Br(),
                                                                    ],
                                                                    #className="d-grid gap-4 col-6 mx-auto",
                                                                    style={'textAlign':'center'}
                                                                ),
                                                            ],
                                                            width=4
                                                        ),
                                                        dbc.Col(width=4)
                                                    ]
                                                ),
                                                dbc.Row(
                                                    children=[
                                                        dbc.Col(width=4),
                                                        dbc.Col(
                                                            children=[
                                                                html.Div(
                                                                    children=[
                                                                        dmc.Button('Download Form', id='button_form',color='darkBlue',size='md'),
                                                                        # dbc.Button(
                                                                        #     'Download Form',
                                                                        #     id='button_form',
                                                                        # ),
                                                                        html.Br(),
                                                                        # html.H6('After completion'),
                                                                        dbc.NavLink('After completion, reupload here.', href='/',style = {'color': 'blue','font-weight':'bold'},className='navlink-parker'),
                                                                    ],
                                                                    className="d-grid gap-3 col-6 mx-auto",
                                                                    style={'textAlign':'center'}
                                                                ),
                                                            ],
                                                            width=4
                                                        ),
                                                        dbc.Col(width=4)
                                                    ]
                                                ),
                                                html.Br(),
                                                html.Br(),
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
                                                                html.Br(),
                                                                html.Div(

                                                                    dbc.Button(
                                                                        dbc.NavLink('Go home', href='/',style = {'color': 'white','font-weight':'bold'},className='navlink-parker'),#,className='nav-link'))
                                                                    ),
                                                                    className="d-grid gap-2 col-6 mx-auto",
                                                                ),
                                                                html.Br(),
                                                                html.Br(),
                                                                
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
                            ],
                            width=10
                        ),
                        dbc.Col(width=1)
                    ]
                ),   
                dmc.Group(
                    position="center",
                    mt="xl",
                    children=[
                        dmc.Button("Prev. step", id="stepper_generate_form_back",color='darkBlue',size='md'),# variant="default"),
                        dmc.Button("Next step", id="stepper_generate_form_next",color='darkBlue',size='md')
                    ],
                ),
            ]
        )
    ]
)
    ]
)


@callback(
    [
        Output(component_id="stepper_generate_form", component_property="active"),
        Output(component_id="generate_step_1_error_div",component_property="children")
        #  Output(component_id="stepper_generate_form", component_property="children")
    ],
    [
        Input(component_id='stepper_generate_form_back', component_property="n_clicks"),
        Input(component_id='stepper_generate_form_next', component_property="n_clicks")
    ],
    [
        State(component_id="stepper_generate_form", component_property="active"),
        # State(component_id="generate_step_1",component_property="children")
        State(component_id="sample_checklist",component_property="value")
        # State(component_id="stepper_generate_form", component_property="children")
    ],
    prevent_initial_call=True
)
def update(stepper_generate_form_back_n_clicks, stepper_generate_form_next_n_clicks, current,sample_checklist_value):

    if ctx.triggered_id=="stepper_generate_form_next":
        if current==0:
            generate_step_1_errors=generate_step_1_error_checker(sample_checklist_value)
            print(generate_step_1_errors)
            print(type(generate_step_1_errors))
            if generate_step_1_errors!=False:
                print('are we in if')
                generate_step_1_error_div_children=html.H6(generate_step_1_errors)
                generate_step_1_error_div_children=dbc.Row(
                    children=[
                        dbc.Col(width=3),
                        dbc.Col(dmc.Alert(generate_step_1_errors,withCloseButton=True),width=6),
                        dbc.Col(width=3)
                    ]
                )
                return [current,generate_step_1_error_div_children]
                
                
    print(ctx.triggered_id)

    if ctx.triggered_id=="stepper_generate_form_back" and current>0:
        current-=1
    elif ctx.triggered_id=="stepper_generate_form_next" and current<NUM_STEPS:
        current+=1        
    # print(step)
    
    # output_children=my_children
    # output_children[current]=my_children[current]


    # return [current,my_children]
    return [current,[]]




@callback(
    [
        Output(component_id="Div_metadata_datatable", component_property="children"),
    ],
    [
        # Input(component_id='stepper_generate_form_back', component_property="n_clicks"),
        # Input(component_id='stepper_generate_form_next', component_property="n_clicks")
        Input(component_id='sample_checklist', component_property='value'),
        # Input(component_id='study_checklist',component_property='value'),
        # Input(component_id="extra_checklist",component_property='value'),
        Input(component_id="sample_count_input",component_property='value'),
        
        Input(component_id="dimension_checklist",component_property='value'),
        Input(component_id="extras_checklist",component_property='value'),
        Input(component_id="factors_checklist",component_property='value'),
        Input(component_id="longitudinal_checklist",component_property='value'),
        Input(component_id="other_checklist",component_property='value'),
    ],
    [
        State(component_id='sample_checklist', component_property='value'),
        # State(component_id='study_checklist',component_property='value'),
        # State(component_id="extra_checklist",component_property='value'),
        State(component_id="sample_count_input",component_property='value'),


        State(component_id="dimension_checklist",component_property='value'),
        State(component_id="extras_checklist",component_property='value'),
        State(component_id="factors_checklist",component_property='value'),
        State(component_id="longitudinal_checklist",component_property='value'),
        State(component_id="other_checklist",component_property='value'),



    ],
    prevent_initial_call=True
)
def update_example_table(a,b,c,d,e,f,g,sample_checklist_values,sample_count_input_value,
    dimension_checklist_value,
    extras_checklist_value,
    factors_checklist_value,
    longitudinal_checklist_value,
    other_checklist_value

):

    #### This should be something different. should probably just generate an empty DT ####
    if sample_checklist_values==None:# and study_checklist_values==None:
        raise PreventUpdate

    if sample_checklist_values==None:
        sample_checklist_values=[]
    # if study_checklist_values==None:
    #     study_checklist_values=[]


    additional_header_checklist_values=list()
    for temp_checklist in [dimension_checklist_value,extras_checklist_value,factors_checklist_value,longitudinal_checklist_value,other_checklist_value]:
        if temp_checklist is not None:
            additional_header_checklist_values+=temp_checklist
    # if extra_checklist_values==None:
    #     extra_checklist_values=[]


    archetype_headers=generate_form_headers(sample_checklist_values)#+study_checklist_values)
    extra_headers=generate_extra_headers(additional_header_checklist_values)
    
    total_headers=archetype_headers+extra_headers
    
    total_columns=[
        {'name':temp_element, 'id':temp_element} for temp_element in total_headers
    ]

    #total_data=list()
    #total_data.append(
    total_data=[
        {
            temp_col['id']:'table preview' for temp_col in total_columns
        }
        for temp_row in range(sample_count_input_value)
    ]

    output_children=[
        dbc.Row(
            children=[
                dbc.Col(width=1),
                dbc.Col(
                    children=[
                        dmc.Center(
                        #html.Div(
                            children=[
                                dash_table.DataTable(
                                    id='dt_for_preview',
                                    columns=total_columns,
                                    data=total_data,
                                    style_cell={
                                        'fontSize': 17,
                                        'padding': '8px',
                                        'textAlign': 'center',
                                        
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
                                        'color':'rgb(211,211,211)',
                                        'font-style':'italic'
                                    },
                                    style_table={
                                        'overflowX': 'scroll'
                                    },
                                    page_action='native',
                                    page_size=3,
                                    fill_width=False,
                                    # virtualization=True
                                )
                            ],#style={"max-width": "600px"}
                            #style={"max-width":"1000px",'textAlign':'center'}
                            #size=1000
                            #style={'textAlign':'center'}
                        )
                    ],
                    width=10
                ),
                dbc.Col(width=1)
            ]
        ),        
    ]

    return [output_children]



def fill_title_sheet(temp_writer,workbook,worksheet):
    worksheet=temp_writer.sheets['Instructions']
    worksheet.hide_gridlines()
    top_format=workbook.add_format({
        'bold': 1,
        'align': 'left',
        'valign': 'vcenter',
        'font_size':16
    })
    rule_format=workbook.add_format({
        'align': 'left',
        'valign': 'vcenter',
        'font_size':16
    })
        
    #write the #first sheet
    worksheet.merge_range('B2:L2','Guidelines',top_format)
    worksheet.merge_range('C4:S4','One Sample Per Row',rule_format)
    worksheet.merge_range('C6:S6','Columns can be empty',rule_format)
    worksheet.merge_range('C8:S8','Use fragments/phrases - not descriptions ("Mediterranean Diet" not "assorted fish, whole grains, plant oils, etc.")',rule_format)
    worksheet.merge_range('C10:S10','For multiples - (multiple drugs, species, etc.) separate with ~ or insert column with same header',rule_format)    

    return workbook, worksheet

def update_excel_sheet_sample_formatting(workbook,worksheet,temp_dataframe):#,group_to_header_dict,group_to_archetype_dict):


    my_format=workbook.add_format({
        'bold': 1,
        'align': 'center',
        'valign': 'vcenter',
        'font_size':8
    })
    # print(worksheet)

    # for i,temp_col in enumerate(temp_dataframe.columns):
    #     proper_text=temp_col.split('-')[0]
    #     worksheet.write(0,i,proper_text,my_format)
    # for i,temp_col in enumerate(temp_dataframe.columns):
    #     #proper_text=temp_col.split('-')[0]
    #     worksheet.write(0,i,temp_col,my_format)

    worksheet.autofit()

    return workbook, worksheet





@callback(
    [
        Output(component_id="download_form", component_property="data"),
    ],
    [
        Input(component_id='button_form', component_property='n_clicks'),
    ],
    [
        #State(component_id="column_store", component_property="data"),
        State(component_id="dt_for_preview",component_property="columns"),
        State(component_id="dt_for_preview",component_property="data"),
    ],
    prevent_initial_call=True
)
# def generate_form(button_form_n_clicks,sample_checklist_options,study_checklist_options):
def generate_form(button_form_n_clicks,dt_for_preview_columns,dt_for_preview_data):
    '''
    creates the form that is downloaded by users
    '''
    print('+++++++++++++++++++++++++++')
    print(button_form_n_clicks)
    print(ctx.triggered_id)
    #a potential improvement would be to generate a visible error if nothing is checked
    if dt_for_preview_columns==None or button_form_n_clicks==None:# and study_checklist_options==None:
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
        {
            element['id']:['' for temp_row in dt_for_preview_data] for element in dt_for_preview_columns
        }
    )

    #we write to bytes because it is much more versatile
    output_stream=io.BytesIO()
    temp_writer=pd.ExcelWriter(output_stream,engine='xlsxwriter')
    #temp_writer=pd.ExcelWriter(output_stream,engine='openpyxl')

    empty_df=pd.DataFrame()
    empty_df.to_excel(temp_writer,sheet_name='Instructions',index=False)

    # print('--------------------------')
    # print(temp_dataframe)

    temp_dataframe.index=[i+1 for i in temp_dataframe.index]
    temp_dataframe.to_excel(temp_writer,sheet_name='sample_sheet')#,index=False)#,startrow=1)



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
    
    ###NEEED TO UPDAT#############3
    workbook, worksheet=update_excel_sheet_sample_formatting(workbook,worksheet,temp_dataframe)#,group_to_header_dict,group_to_archetype_dict)
    workbook, worksheet=fill_title_sheet(temp_writer,workbook,worksheet)

    temp_writer.save()
    temp_data=output_stream.getvalue()

    return [
        dcc.send_bytes(temp_data,"binbase_sample_ingestion_form.xlsx")
    ]