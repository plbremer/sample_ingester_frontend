
import dash
from dash import dcc, html,dash_table,callback, ctx,MATCH,ALL
import plotly.express as px
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import dash_mantine_components as dmc


import numpy as np

NUM_STEPS=3


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

        dbc.Row(
            children=[
                dbc.Col(width=3),
                dbc.Col(
                    children=[
                        html.H6('hi')
                    ]
                )
            ]
        ),

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
                            description="Verify email",
                            children=dmc.Text("1th content", align="center"),
                        ),
                        
                        dmc.StepperStep(
                            label="third step",
                            description="asdfgasdfg",
                            children=[
                                dmc.Text("2th content", align="center"),
                                dbc.Checklist(
                                    options=[
                                        {"label": "Tissue (lung, heart, etc.)", "value": 'tissue'},
                                        {"label": "Biofluids (plasma, urine, etc.)", "value": 'fluid'},
                                        {"label": "Cells (culture, organoid, etc.)", "value": 'cells'},
                                        {"label": "Raw Material (soil, water, gas, etc.)", "value": 'raw_material'},
                                    ],
                                    id="sample_checklist",
                                ),
                            ]
                        ),
                        dmc.StepperCompleted(
                            children=dmc.Text(
                                "Completed, click back button to get to previous step",
                                align="center",
                            )
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