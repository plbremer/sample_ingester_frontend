

import dash
from dash import dcc, html,callback
from dash.dependencies import Input, Output, State

import plotly.express as px
import dash_bootstrap_components as dbc

from dash.exceptions import PreventUpdate

import pandas as pd

import xlsxwriter
from xlsxwriter.utility import xl_rowcol_to_cell

import base64
import io
from pprint import pprint

dash.register_page(__name__, path='/download-and-resubmit')

FORM_HEADER_DICT={
    'tissue':['species','organ','sex','height','heightUnit','weight','weightUnit','age','ageUnit','mass','massUnit','otherInclusionCriteria','otherExclusionCriteria'],
    'fluid':['species','organ','sex','height','heightUnit','weight','weightUnit','age','ageUnit','volume','volumeUnit','otherInclusionCriteria','otherExclusionCriteria'],
    'cells':['species','cell_line','cell_count','otherInclusionCriteria','otherExclusionCriteria'],
    'raw_material':['material','mass','massUnit','volume','volumeUnit','otherInclusionCriteria','otherExclusionCriteria'],
    'genetic':['gene'],
    'longitudinal':['zeroTimeEvent','time','timeUnit'],
    'intervention':['drugName','drugDoseVolumeOrMass','drugDoseUnit','diet','exercise'],
    'effect':['disease'],
    #'general':[,'otherInclusionCriteria','otherExclusionCriteria']
}

#FORM_HEADER_DICT_REVERSE={}
FORM_HEADER_DICT_REVERSE={element:set() for element in sum(FORM_HEADER_DICT.values(),[])}
for temp_archetype in FORM_HEADER_DICT.keys():
    for temp_header in FORM_HEADER_DICT[temp_archetype]:
        FORM_HEADER_DICT_REVERSE[temp_header].add(temp_archetype)
#print(FORM_HEADER_DICT_REVERSE)
#hold=input('reverse dict')

def generate_form_headers(selected_archetypes):
    '''
    a more sophisticated approach needs to be implemented.
    should probably read from a support file.
    need to make it so that properties dont appear multiple times
    '''
    # form_header_dict={
    #     'tissue':['species','organ','sex','height','heightUnit','weight','weightUnit','age','ageUnit','otherInclusionCriteria','otherExclusionCriteria'],
    #     'fluid':['species','organ','sex','height','heightUnit','mass','massUnit','age','ageUnit','otherInclusionCriteria','otherExclusionCriteria'],
    #     'cells':['species','cell_line','cell_count','otherInclusionCriteria','otherExclusionCriteria'],
    #     'raw_material':['material','mass','massUnit','volume','volumeUnit','otherInclusionCriteria','otherExclusionCriteria'],
    #     'genetic':['gene'],
    #     'longitudinal':['zeroTimeEvent','time','timeUnit'],
    #     'intervention':['drugName','drugDoseVolumeOrMass','drugDoseUnit','diet','exercise'],
    #     'effect':['disease'],
    #     #'general':[,'otherInclusionCriteria','otherExclusionCriteria']
    # }

    total_headers=[]
    for temp_header in selected_archetypes:
        for temp_element in FORM_HEADER_DICT[temp_header]:
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
                                {"label": "Tissue (lung, heart, etc.)", "value": 'tissue'},
                                {"label": "Biofluids (plasma, urine, etc.)", "value": 'fluid'},
                                {"label": "Cells (culture, organoid, etc.)", "value": 'cells'},
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
                                {"label": "Genetic (knockout, CRISPR, MIR, etc.)", "value": 'genetic'},
                                {"label": "Time Series (longitudinal)", "value": 'longitudinal'},
                                {"label": "Intervention (drug, diet, exercise, etc.)", "value": 'intervention'},
                                {"label": "Effect (disease, etc.)", "value": 'effect'},
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
                dbc.Col(width=4),
                dbc.Col(
                    children=[
                        dcc.Upload(
                            id='upload_form',
                            children=html.Div([
                                'Drag and Drop or Select Files',
                                #html.A('Select Files')
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


def generate_header_colors(selected_archetypes,total_headers):
    '''
    the goal of this method is to generate the header colors :)
    '''
    print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    
    #selected_archetypes=set(selected_archetypes)
    #total_headers=set(total_headers)
    print(total_headers)
    print('')
    #hold=input('here')
    header_to_archetype_dict=dict()
    for header in total_headers:
        print(header)
        print(FORM_HEADER_DICT_REVERSE[header].intersection(selected_archetypes))
        header_to_archetype_dict[header]=FORM_HEADER_DICT_REVERSE[header].intersection(set(selected_archetypes))
    #now we have {header:{archetypes}} over headers
    #we want to group these sets (we want the reverse of this {{archetypes}:header})
    #but we cannot use sets as keys
    #so we settle for a scheme
    #{group_number:[headers]}
    #combined with
    #{group_number:[archetypes]}
    #first we get the group number keys
    #this is a list of archtypes [archetypes]
    print(FORM_HEADER_DICT_REVERSE)
    print('')
    print(header_to_archetype_dict)
    print('')
    unique_groups=[]
    for header in header_to_archetype_dict.keys():
        #if the archetype set is not in unique groups
        if header_to_archetype_dict[header] not in unique_groups:
            unique_groups.append(header_to_archetype_dict[header])
    #now for each unique group, get the list of headers associated
    group_to_header_dict={i:list() for i in range(len(unique_groups))}
    for temp_header in header_to_archetype_dict:
        temp_group_number=unique_groups.index(header_to_archetype_dict[temp_header])
        group_to_header_dict[temp_group_number].append(temp_header)
    #{group_number:[archetypes]} is the same thing as the unique groups list
    group_to_archetype_dict={i:element for i,element in enumerate(unique_groups)}

    # print(group_to_header_dict)
    # print('')
    # print(group_to_archetype_dict)
    # hold=input('both dictionaries')
    return group_to_header_dict,group_to_archetype_dict



    
        


    





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

    group_to_header_dict,group_to_archetype_dict=generate_header_colors(sample_checklist_options+study_checklist_options,total_headers)
    pprint(group_to_header_dict)
    pprint(group_to_archetype_dict)
    #need to rearrange columns to match group order
    #then put dataframe one level lower
    column_order_list=sum(group_to_header_dict.values(),[])


    temp_dataframe=pd.DataFrame.from_dict(
        {element:[] for element in column_order_list}
    )
    print(temp_dataframe)
    

    output_stream=io.BytesIO()
    temp_writer=pd.ExcelWriter(output_stream,engine='xlsxwriter')

    empty_df=pd.DataFrame()
    empty_df.to_excel(temp_writer,sheet_name='title_page',index=False)
    temp_dataframe.to_excel(temp_writer,sheet_name='sample_sheet',index=False,startrow=1)

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
    color_list=['red','orange','yellow','green','lime','sky','khaki','red','orange','yellow','green','lime','sky','khaki','red','orange','yellow','green','lime','sky','khaki']
    merge_format_dict=dict()
    for group_id in group_to_header_dict.keys():
        merge_format_dict[group_id]=workbook.add_format(
            {
                #'bold': 1,
                #'border': 1,
                'align': 'center',
                'valign': 'vcenter',
                'fg_color': color_list[group_id]
            }
        )
    start_cell=0
    for group_id in merge_format_dict.keys():
        #start_cell=lhs
        
        end_cell=start_cell+len(group_to_header_dict[group_id])-1
        if (end_cell-start_cell)>=1:
            start_cell_xl=xl_rowcol_to_cell(0,start_cell)
            end_cell_xl=xl_rowcol_to_cell(0,end_cell)
            start_cell=start_cell+len(group_to_header_dict[group_id])
            merge_string='Associated with: '+(', '.join(group_to_archetype_dict[group_id]))
            worksheet.merge_range(
                start_cell_xl+':'+end_cell_xl,
                merge_string,
                merge_format_dict[group_id]
            )
        elif (end_cell-start_cell)==0:
            start_cell_xl=xl_rowcol_to_cell(0,start_cell)
            end_cell_xl=xl_rowcol_to_cell(0,end_cell)
            start_cell=start_cell+len(group_to_header_dict[group_id])
            non_merge_string='Associated with: '+(', '.join(group_to_archetype_dict[group_id]))
            worksheet.write(start_cell_xl,non_merge_string,merge_format_dict[group_id])
            # worksheet.add_format(
            #     merge_format_dict[group_id]
            # )


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
        #we used to ahve the div_filename as the output property, now we change the children of the upload
        #Output(component_id="div_filename", component_property="children"),
        Output(component_id="upload_form",component_property="children"),
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
        sheet_name='sample_sheet',
        skiprows=1
        #index_col=False
    )

    print(temp_dataframe)

    temp_dataframe_as_json=temp_dataframe.to_json(orient='records')

    print(temp_dataframe_as_json)
    displayed_name=html.Div([upload_form_filename],className='text-center')
    return [displayed_name,temp_dataframe_as_json]


                        # upload_form',
                        #     children=html.Div([
                        #         'Drag and Drop or Select Files',
                        #         #html.A('Select Files')
                        #     ]),