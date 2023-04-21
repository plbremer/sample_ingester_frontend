from dash import dcc, html,dash_table,callback, ctx,MATCH,ALL
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import dash


import numpy as np
import pandas as pd
from xlsxwriter.utility import xl_rowcol_to_cell
import json
import base64
import io
from pprint import pprint
import requests

from . import samplemetadatauploadchecker


dash.register_page(__name__, path='/submit-form')

BASE_URL_API = "http://127.0.0.1:4999/"

with open('assets/form_header_dict_basics.json','r') as f:
    FORM_HEADER_DICT=json.load(f)
with open('assets/extra_columns.json','r') as f:
    EXTRA_COLUMNS=json.load(f)

NUM_STEPS_2=5
SPLIT_CHAR='~'
NEIGHBORS_TO_RETRIEVE=100


with open('additional_files/subset_per_heading.json', 'r') as fp:
    subset_per_heading_json=json.load(fp)


def generate_all_columns(list_of_jsons_value_lists_are_potential_columns):

    total_valid_columns=set()
    for temp_json in list_of_jsons_value_lists_are_potential_columns:
        for temp_key in temp_json:
            for temp_header in temp_json[temp_key]:
                total_valid_columns.add(temp_header)

    return total_valid_columns
ALL_METADATA_COLUMNS=generate_all_columns([FORM_HEADER_DICT,EXTRA_COLUMNS])


def parse_stored_excel_file(store_panda):
    '''
    extracts the {header:[written_string]} relationship
    '''
    temp_header_dict=dict()
    for temp_header in store_panda.columns:
        temp_header_dict[temp_header]=store_panda[temp_header].dropna().unique().tolist()
    #split inefficiently so that we can just comment out the next part if we desire

    output_dict=dict()
    for temp_key in temp_header_dict.keys():
        output_dict[temp_key.split('.')[0]]=list()
    # print(output_dict)

    for temp_key in temp_header_dict.keys():
        # print(temp_key)
        # print(output_dict[temp_key.split('.')[0]])
        # print(output_dict[temp_key])
        output_dict[temp_key.split('.')[0]] = output_dict[temp_key.split('.')[0]] + temp_header_dict[temp_key]
    


    return output_dict

def split_columns_if_delimited(temp_dataframe):
    #for each column
    #split it
    #delete the orignal
    #append the new ones
    #much easier to conserve the order than to reorder
    #do in parallel with temp_dataframe_2
    new_dataframe_list=list()
    #new_dataframe_list_2=list()
    for temp_column in temp_dataframe.columns:
        if temp_dataframe[temp_column].dtype==object:
            #num_cols_after_split=len(temp_dataframe[temp_column].str.split(SPLIT_CHAR,expand=True))
            temp_expanded_columns=temp_dataframe[temp_column].str.split(SPLIT_CHAR,expand=True).add_prefix(temp_column+'.')
            #temp_expanded_columns_2=temp_dataframe_2
        else:
            temp_expanded_columns=temp_dataframe[temp_column]
        new_dataframe_list.append(temp_expanded_columns)

    output_dataframe=pd.concat(new_dataframe_list,axis='columns')
    output_dataframe.fillna(value=np.nan,inplace=True)

    return output_dataframe




layout = html.Div(
    children=[
        # html.H6('hi')
        # dcc.Download(id="download_curated_form"),
        # html.Br(),
        # html.Br(),
        # dbc.Row(
        #     children=[
        #         html.Div(
        #             id='here_is_where_we_put_the curation_interface'
        #         )
        #     ]
        # ),
        # html.Br(),
        # html.Br(),
        # dbc.Row(
        #     children=[
        #         html.Div(
        #             dbc.Button(
        #                 'Download Curated Form',
        #                 id='button_download_curated',
        #             ),
        #             className="d-grid gap-2 col-6 mx-auto",
        #         ),
        #     ]
        # ),
        # html.Br(),
        # html.Br(),
        # html.Div(id='Div_new_vocab_error_messages'),
        dcc.Store('upload_store'),
        dcc.Store('store_2'),
        dcc.Store('store_3'),
        html.Br(),
        html.Br(),
        html.Br(),
        html.Br(),

        html.Div(
            children=[
                

                dbc.Row(
                    children=[
                        dbc.Col(width=1),
                        dbc.Col(
                            children=[
                                


                                dmc.Stepper(
                                    id="stepper_submit_form",
                                    active=0,
                                    breakpoint="sm",
                                    children=[
                                        dmc.StepperStep(
                                            id='step_1',
                                            label="First step",
                                            description="Choose Archetypes",
                                            children=[
                                                html.Div(id='Div_curate_button_or_error_messages'),
                                                dbc.Row(
                                                    children=[
                                                        dbc.Col(width=4),
                                                        dbc.Col(
                                                            children=[
                                                                dcc.Upload(
                                                                    id='upload_form',
                                                                    children=html.Div([
                                                                        'Upload Completed Form',
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
                                                            width=4
                                                        ),
                                                        dbc.Col(width=4)
                                                    ]
                                                ),                                                
                                            ]
                                        ),
                                        dmc.StepperStep(
                                            id='step_2',
                                            label="Second step",
                                            description="Extra Specifications",
                                            children=[
                                                html.H6('second step')
                                                
                                            ] 
                                        ),
                                        dmc.StepperStep(
                                            id='step_3',
                                            label="3 step",
                                            description="Extra Specifications",
                                            children=[
                                                html.H6('3 step')
                                                
                                            ] 
                                        ),
                                        dmc.StepperStep(
                                            id='step_4',
                                            label="4 step",
                                            description="Extra Specifications",
                                            children=[
                                                html.H6('4 step')
                                                
                                            ] 
                                        ),
                                        dmc.StepperStep(
                                            id='step_5',
                                            label="5 step",
                                            description="Extra Specifications",
                                            children=[
                                                html.H6('5 step')
                                                
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
                                    ]
                                )
                            ]
                        )
                    ]
                ),
                dmc.Group(
                    position="center",
                    mt="xl",
                    children=[
                        dbc.Button("Prev. step", id="stepper_submit_form_back"),# variant="default"),
                        dbc.Button("Next step", id="stepper_submit_form_next")
                    ],
                ),
            ]
        )
    ],
)

@callback(
    [
        Output(component_id="stepper_submit_form", component_property="active"),
        

        Output(component_id="store_2", component_property="data"),
        Output(component_id="store_3", component_property="data"),

        Output(component_id="step_2", component_property="children"),
        Output(component_id="step_3", component_property="children"),


        

        #Output(component_id="stepper_submit_form", component_property="children")

    ],
    [
        Input(component_id='stepper_submit_form_back', component_property="n_clicks"),
        Input(component_id='stepper_submit_form_next', component_property="n_clicks")
    ],
    [
        State(component_id="stepper_submit_form", component_property="active"),
        # State(component_id="stepper_submit_form", component_property="children")
        State(component_id="upload_store", component_property="data"),
        State(component_id="store_2", component_property="data"),
        State(component_id="store_3", component_property="data"),
        #State(component_id="store_4", component_property="data"),
        State(component_id="step_2", component_property="children"),
        State(component_id="step_3", component_property="children"),
        # Output(component_id="step_4", component_property="children"),
        State(component_id={'type':'step_2_curation_checkbox','index':ALL}, component_property="checked"),
    ],
    prevent_initial_call=True
)
def update_step_submit(
    stepper_submit_form_back_n_clicks, 
    stepper_submit_form_next_n_clicks, 
    current,
    upload_store_data,
    store_2_data,
    store_3_data,
    step_2_children,
    step_3_children,
    step_2_curation_checkbox_n_clicks_ALL
    
):#,my_children):
    '''
    we wnat to only do work according to the step that we are outputting
    for example, we only want to output the step_2_children if current becomes 1
    '''
    if ctx.triggered_id=="stepper_submit_form_back" and current>0:
        current-=1
    elif ctx.triggered_id=="stepper_submit_form_next" and current<NUM_STEPS_2:
        current+=1   
    # current+=1

    upload_store_panda=pd.read_json(upload_store_data['input_dataframe'],orient='records')
    '''
        species.0 species.1.0 species.1.1 organ.0
    0     humen       mouse   porcupine   liver
    1     humen        mouo        None   lunge
    '''
    print(upload_store_panda)
    written_strings_per_category=parse_stored_excel_file(upload_store_panda)
    '''
    {'organ': ['liver', 'lunge'],
    'species': ['humen', 'mouse', 'mouo', 'porcupine']}
    '''
    pprint(written_strings_per_category)

    #if we enter step 2
    if current==1:
        panda_for_store_2,step_2_children=generate_step_2_layout_and_data_for_store(written_strings_per_category)
        store_2_data=panda_for_store_2.to_dict(orient='records')
        print(store_2_data)       
        #print(dict_for_store_2)
        print(pd.DataFrame.from_records(store_2_data))
        print('&'*20)
    #curation_dict,output_children
    #elif current!=1:
    elif current==2:
        print(step_2_curation_checkbox_n_clicks_ALL)
        step_3_children=generate_step_3_layout_and_data_for_store(
            store_2_data,
            step_2_curation_checkbox_n_clicks_ALL,
        )



    return [current,store_2_data,store_3_data,step_2_children,step_3_children]

def generate_step_3_layout_and_data_for_store(store_2_data,step_2_curation_checkbox_n_clicks_ALL):
    print('in step 3')
    print(step_2_curation_checkbox_n_clicks_ALL)
    store_2_panda=pd.DataFrame.from_records(store_2_data)
    print(store_2_panda)
    written_strings_to_substring_panda=store_2_panda.loc[step_2_curation_checkbox_n_clicks_ALL]
    if len(written_strings_to_substring_panda.index)==0:
        print('need to figure this out')
        output_children=html.H3('need to figure out when there are no curations to do')
    else:
        output_children=list()

        output_children.append(
            dbc.Row(
                children=[
                    dbc.Col(
                        html.H3('Metadata Header')
                    ),    
                    dbc.Col(
                        html.H3('Written String')
                    ),
                    dbc.Col(
                        html.H3('Substring Search')
                    ),   
                    dbc.Col(
                        html.H3('None existent?') 
                    ),
                ]
            )
        )
        #for temp_header in curation_dict.keys():
        for temp_group in written_strings_to_substring_panda.groupby('header'):
            
            for i,(index,series) in enumerate(temp_group[1].iterrows()):
                if i==0:
                    output_children.append(
                        dbc.Row(
                            children=[
                                dbc.Col(
                                    html.H6(series['header'])
                                ),    
                                dbc.Col(
                                    html.H6(series['written_string'])
                                ),
                                # dbc.Col(
                                #     html.H6(
                                #         curation_dict[temp_header][temp_written_string]['valid_string']+' AKA '+curation_dict[temp_header][temp_written_string]['main_string']
                                #     )
                                # ),   
                                dbc.Col(
                                    dcc.Dropdown(
                                        id={
                                            'type':'dropdown_empty_options',
                                            'index':series['header']+'_'+series['written_string']
                                        },
                                        multi=False,
                                        placeholder='Type compound name to search',
                                        options=['Type substring to populate options.'],
                                        optionHeight=60
                                    ),  
                                ),
                                dbc.Col(
                                    dmc.Checkbox(
                                        id={
                                            'type':'step_3_curation_checkbox',
                                            'index':series['header']+'_'+series['written_string']
                                        },
                                        # multi=False,
                                        # #placeholder='Type compound name to search',
                                        # options=['Type substring to populate options.'],
                                        # optionHeight=60
                                        checked=False
                                    ),  
                                ),
                            ]
                        )
                    )
                else:
                    output_children.append(
                        dbc.Row(
                            children=[
                                dbc.Col(
                                    html.H6(' ')
                                ),    
                                dbc.Col(
                                    html.H6(series['written_string'])
                                ),
                                # dbc.Col(
                                #     html.H6(
                                #         curation_dict[temp_header][temp_written_string]['valid_string']+' AKA '+curation_dict[temp_header][temp_written_string]['main_string']
                                #     )
                                # ),   
                                dbc.Col(
                                    dcc.Dropdown(
                                        id={
                                            'type':'dropdown_empty_options',
                                            'index':series['header']+'_'+series['written_string']
                                        },
                                        multi=False,
                                        placeholder='Type compound name to search',
                                        options=['Type substring to populate options.'],
                                        optionHeight=60
                                    ),  
                                ),
                                dbc.Col(
                                    dmc.Checkbox(
                                        id={
                                            'type':'step_3_curation_checkbox',
                                            'index':series['header']+'_'+series['written_string']
                                        },
                                        # multi=False,
                                        # #placeholder='Type compound name to search',
                                        # options=['Type substring to populate options.'],
                                        # optionHeight=60
                                        checked=False
                                    ),  
                                ),
                            ]
                        )
                    )


    return output_children

               




def generate_step_2_layout_and_data_for_store(written_strings_per_category):

    curation_dict=dict()
    #get curation proposals
    for temp_header in written_strings_per_category.keys():

        if temp_header not in subset_per_heading_json.keys():
            continue
        curation_dict[temp_header]=dict()

        for temp_written_string in written_strings_per_category[temp_header]:

            prediction_request={
                "header":temp_header,
                "written_strings":[temp_written_string],
                "neighbors_to_retrieve":NEIGHBORS_TO_RETRIEVE
            }

            response = requests.post(BASE_URL_API + "/predictvocabularytermsresource/", json=prediction_request)
            this_strings_neighbors = pd.read_json(response.json(), orient="records")  
        
            #print(this_strings_neighbors)
            curation_dict[temp_header][temp_written_string]={
                'main_string':this_strings_neighbors.at[0,'main_string'],
                'valid_string':this_strings_neighbors.at[0,'valid_string']
            }
    




        #for 
    output_children=list()

    output_children.append(
        dbc.Row(
            children=[
                dbc.Col(
                    html.H3('Metadata Header')
                ),    
                dbc.Col(
                    html.H3('Written String')
                ),
                dbc.Col(
                    html.H3('Curated String')
                ),   
                dbc.Col(
                    html.H3('Curation Wrong?') 
                ),
            ]
        )
    )
    for temp_header in curation_dict.keys():

        for i,temp_written_string in enumerate(curation_dict[temp_header]):
            if i==0:
                output_children.append(
                    dbc.Row(
                        children=[
                            dbc.Col(
                                html.H6(temp_header)
                            ),    
                            dbc.Col(
                                html.H6(temp_written_string)
                            ),
                            dbc.Col(
                                html.H6(
                                    curation_dict[temp_header][temp_written_string]['valid_string']+' AKA '+curation_dict[temp_header][temp_written_string]['main_string']
                                )
                            ),   
                            dbc.Col(
                                dmc.Checkbox(
                                    id={
                                        'type':'step_2_curation_checkbox',
                                        'index':str(temp_header)+'_'+str(temp_written_string)
                                    },
                                    # multi=False,
                                    # #placeholder='Type compound name to search',
                                    # options=['Type substring to populate options.'],
                                    # optionHeight=60
                                    checked=False
                                ),  
                            ),
                        ]
                    )
                )
            else:
                output_children.append(
                    dbc.Row(
                        children=[
                            dbc.Col(
                                html.H6(' ')
                            ),    
                            dbc.Col(
                                html.H6(temp_written_string)
                            ),
                            dbc.Col(
                                html.H6(
                                    curation_dict[temp_header][temp_written_string]['valid_string']+' AKA '+curation_dict[temp_header][temp_written_string]['main_string']
                                )
                            ),   
                            dbc.Col(
                                dmc.Checkbox(
                                    id={
                                        'type':'step_2_curation_checkbox',
                                        'index':str(temp_header)+'_'+str(temp_written_string)
                                    },
                                    # multi=False,
                                    # #placeholder='Type compound name to search',
                                    # options=['Type substring to populate options.'],
                                    # optionHeight=60
                                    checked=False
                                ),  
                            ),
                        ]
                    )
                )

    curation_panda_dict={
        'header':[],
        'written_string':[],
        'valid_string':[],
        'main_string':[]
    }
    for temp_header in curation_dict.keys():
        # output_children.append(
        #     dbc.Row(
        #         children=[
        #             dbc.Col(
        #                 html.H3(temp_header)
        #             )
        #         ]
        #     )
        # )
        for temp_written_string in (curation_dict[temp_header]):
            curation_panda_dict['header'].append(temp_header)
            curation_panda_dict['written_string'].append(temp_written_string)
            curation_panda_dict['valid_string'].append(curation_dict[temp_header][temp_written_string]['valid_string'])
            curation_panda_dict['main_string'].append(curation_dict[temp_header][temp_written_string]['main_string'])
    curation_panda=pd.DataFrame.from_dict(curation_panda_dict)
    
    return curation_panda,output_children





# @callback(
#     [
#         Output(component_id="store_2", component_property="data"),
#         # State(component_id="store_3", component_property="data"),
#         # State(component_id="store_4", component_property="data"),
#         # Output(component_id="stepper_submit_form", component_property="active"),
#         # Output(component_id="step_2", component_property="children"),
#         # Output(component_id="step_3", component_property="children"),
#         # Output(component_id="step_4", component_property="children"),

#         #Output(component_id="stepper_submit_form", component_property="children")

#     ],
#     [
#         Input(component_id={'type':'step_2_curation_checkbox','index':ALL}, component_property="checked"),
#         # Input(component_id='stepper_submit_form_next', component_property="n_clicks")
#     ],
#     [
#     #     State(component_id="stepper_submit_form", component_property="active"),
#     #     # State(component_id="stepper_submit_form", component_property="children")
#         State(component_id="upload_store", component_property="data"),
#     #     # State(component_id="store_2", component_property="data"),
#     #     #State(component_id="store_3", component_property="data"),
#     #     #State(component_id="store_4", component_property="data"),
#     #     State(component_id="step_2", component_property="children"),
#     #     # Output(component_id="step_3", component_property="children"),
#     #     # Output(component_id="step_4", component_property="children"),
#     ],
#     prevent_initial_call=True
# )

# def update_step_stores(step_2_curation_checkbox_n_clicks_ALL,upload_store_data):
#     print(ctx.triggered_id)
#     print('in update stores')
#     print(step_2_curation_checkbox_n_clicks_ALL)
#     parse_stored_excel_file


@callback(
    [
        Output(component_id="upload_form",component_property="children"),
        Output(component_id="upload_store",component_property="data"),
        Output(component_id="Div_curate_button_or_error_messages",component_property="children"),
    ],
    [
        Input(component_id="upload_form", component_property="contents"),
    ],
    [
        State(component_id="upload_form", component_property="filename"),
    ],
    prevent_initial_call=True
)
def upload_form(
    upload_form_contents,
    upload_form_filename,
):
    if upload_form_contents==None:
        raise PreventUpdate
    
    '''
    accept the form back from the user
    need to have a more fully fledged format-checking and error throwing suite
    '''

    content_type, content_string = upload_form_contents.split(',')

    #declare instance of upload error tester here
    #run through error tests. excel tests first
    #the error checker returns False for each condition that doesnt have a problem
    #so we check for each problem, and if they are all false, move on to the next situation
    my_SampleMetadataUploadChecker=samplemetadatauploadchecker.SampleMetadataUploadChecker(
        content_string,
        # FORM_HEADER_DICT
        # header_button_column_relationships
        ALL_METADATA_COLUMNS
    )
    excel_sheet_checks=list()
    excel_sheet_checks.append(my_SampleMetadataUploadChecker.create_workbook())
    if excel_sheet_checks[0]==False:
        excel_sheet_checks.append(my_SampleMetadataUploadChecker.lacks_sheetname())
    if any(map(lambda x: isinstance(x,str),excel_sheet_checks)):
        curate_button_children=dbc.Row(
            children=[
                dbc.Col(width=4),
                dbc.Col(
                    children=[html.H6(element,style={'color':'red','text-align':'center'}) for element in excel_sheet_checks if element!=False],
                    width=4,
                ),
                dbc.Col(width=4)
            ]
        )
        store_dict=None
    else:
        dataframe_checks=list()
        my_SampleMetadataUploadChecker.create_dataframe()
        dataframe_checks.append(my_SampleMetadataUploadChecker.headers_malformed())
        dataframe_checks.append(my_SampleMetadataUploadChecker.contains_underscore())
        dataframe_checks.append(my_SampleMetadataUploadChecker.contains_no_sample_rows())
        if any(map(lambda x: isinstance(x,str),dataframe_checks)):
            curate_button_children=dbc.Row(
                children=[
                    dbc.Col(width=4),
                    dbc.Col(
                        children=[html.H6(element,style={'color':'red','text-align':'center'}) for element in dataframe_checks if element!=False],
                        width=4,
                    ),
                    dbc.Col(width=4)
                ]
            )
            
            store_dict=None

        #if there are no problems with the excel file or dataframe
        else:
            curate_button_children=dbc.Row(
                children=[
                    dbc.Col(width=5),
                    dbc.Col(
                        children=[
                            html.H6('form passes checks')
                            # dcc.Link(
                            #     children=[                        
                            #         html.Div(
                            #             dbc.Button(
                            #                 'Process Form',
                            #                 id='button_form',
                            #             ),
                            #             className="d-grid gap-2 col-6 mx-auto",
                            #         ),
                            #     ],
                            #     href='/curate-and-download',
                            # )
                        ],
                        width=2
                    ),
                    dbc.Col(width=5)
                ]
            )

            decoded=base64.b64decode(content_string)
            temp_dataframe=pd.read_excel(
                io.BytesIO(decoded),
                sheet_name='sample_sheet',
                #skiprows=1
            )
            # temp_dataframe_2=pd.read_excel(
            #     io.BytesIO(decoded),
            #     sheet_name='sample_sheet',
            #     header=None,
            #     nrows=1
            # )
            #need to set the temp_dataframe_2 headers to be those from the temp_dataframe in order for the concat to work
            # temp_dataframe_2.columns=temp_dataframe.columns
            # temp_dataframe=pd.concat(
            #     [temp_dataframe,temp_dataframe_2],
            #     axis='index',
            #     ignore_index=True
            # )
            temp_dataframe=split_columns_if_delimited(temp_dataframe)
            temp_dataframe_as_json=temp_dataframe.to_json(orient='records')


            print(temp_dataframe)
            
            store_dict={
                'input_dataframe':temp_dataframe_as_json,
            }

    displayed_name=html.Div([upload_form_filename],className='text-center')
    return [displayed_name,store_dict,curate_button_children]