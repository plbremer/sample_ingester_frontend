from csv import excel
from . import samplemetadatauploadchecker

import dash
from dash import dcc, html,callback, ALL, MATCH, ctx, dash_table
from dash.dependencies import Input, Output, State
import plotly.express as px
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate

import numpy as np
import pandas as pd
from xlsxwriter.utility import xl_rowcol_to_cell
import json
import base64
import io
from random import randint

import xlsxwriter

from pprint import pprint

dash.register_page(__name__, path='/download-and-resubmit')

# #we call the keys here "archetypes"
# with open('assets/form_header_dict.json','r') as f:
#     FORM_HEADER_DICT=json.load(f)

# #obtain the reverse of the FORM_HEADER_DICT, eg {'species:['tissue','fluid','cells']}
# FORM_HEADER_DICT_REVERSE={element:set() for element in sum(FORM_HEADER_DICT.values(),[])}
# for temp_archetype in FORM_HEADER_DICT.keys():
#     for temp_header in FORM_HEADER_DICT[temp_archetype]:
#         FORM_HEADER_DICT_REVERSE[temp_header].add(temp_archetype)

SPLIT_CHAR='~'

# COLOR_LIST=['red','orange','yellow','green','lime','sky','khaki','red','orange','yellow','green','lime','sky','khaki','red','orange','yellow','green','lime','sky','khaki']
    



with open('assets/form_header_dict_accordion.json','r') as f:
    FORM_HEADER_DICT=json.load(f)

# header_button_names=set()
# for level_1 in FORM_HEADER_DICT.keys():
#     for level_2 in FORM_HEADER_DICT[level_1].keys():
#         header_button_names=header_button_names.union(set(FORM_HEADER_DICT[level_1][level_2].keys()))
# print(header_button_names)
# [print(element) for element in FORM_HEADER_DICT['sample']['tissue'].keys()]

header_button_column_relationships=dict()
header_buttons=dict()
for level_1 in FORM_HEADER_DICT.keys():
    for level_2 in FORM_HEADER_DICT[level_1].keys():
        for level_3 in FORM_HEADER_DICT[level_1][level_2].keys():
        #header_buttons[]
        # print(level_2)
            header_button_column_relationships[level_3]=FORM_HEADER_DICT[level_1][level_2][level_3]

            # header_buttons[level_2+'_'+level_3]=html.Div(dbc.Button(level_3,id={'type':'header_button','index':level_2+'_'+level_3}))
            header_buttons[level_2+'_'+level_3]=dbc.Button(level_3,id={'type':'header_button','index':level_2+'_'+level_3})

print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
print(header_button_column_relationships)

# def generate_form_headers(selected_archetypes):
#     '''
#     from the selected archetypes ('tissue', 'genetic', etc.)
#     create the total set of metadata headers. order matters 
#     '''
#     total_headers=[]
#     for temp_header in selected_archetypes:
#         for temp_element in FORM_HEADER_DICT[temp_header]:
#             if temp_element not in total_headers:
#                 total_headers.append(temp_element)
    
#     return total_headers


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
                        # dbc.Collapse(
                        #     dbc.
                        # )
                        # dbc.Button(
                        #     "Tissue (lung, heart, etc.)",
                        #     id="collapse_tissue",
                        #     className="mb-3",
                        #     color="primary",
                        #     n_clicks=0,
                        # ),
                        # html.Br(),
                        # dbc.Button(
                        #     "Biofluids (plasma, urine, etc.)",
                        #     id="collapse_biofluids",
                        #     className="mb-3",
                        #     color="primary",
                        #     n_clicks=0,
                        # ),
                        # html.Br(),
                        # dbc.Button(
                        #     "Cells (culture, organoid, etc.)",
                        #     id="collapse_cells",
                        #     className="mb-3",
                        #     color="primary",
                        #     n_clicks=0,
                        # ),
                        # html.Br(),
                        # dbc.Button(
                        #     "Raw Material (soil, water, gas, etc.)",
                        #     id="collapse_rawmaterial",
                        #     className="mb-3",
                        #     color="primary",
                        #     n_clicks=0,
                        # ),
                        
                        dbc.Accordion(
                            [
                                dbc.AccordionItem(
                                    [
                                        #html.Div(dbc.Button(element),style={'padding':5}) for element in FORM_HEADER_DICT['sample']['tissue'].keys()
                                        header_buttons['tissue_'+element] for element in FORM_HEADER_DICT['sample']['tissue'].keys()
                                    ],
                                    title="Tissue (lung, heart, etc.)",
                                ),
                                dbc.AccordionItem(
                                    [
                                        # dbc.Button(element,id=element) for element in FORM_HEADER_DICT['sample']['fluid'].keys()
                                        header_buttons['fluid_'+element] for element in FORM_HEADER_DICT['sample']['fluid'].keys()
                                    ],
                                    title="Biofluids (plasma, urine, etc.)",
                                ),
                                dbc.AccordionItem(
                                    [
                                        # dbc.Button(element,id=element) for element in FORM_HEADER_DICT['sample']['cells'].keys()
                                        header_buttons['cells_'+element] for element in FORM_HEADER_DICT['sample']['cells'].keys()
                                    ],
                                    title="Cells (culture, organoid, etc.)",
                                ),
                                dbc.AccordionItem(
                                    [
                                        # dbc.Button(element,id=element) for element in FORM_HEADER_DICT['sample']['rawMaterial'].keys()
                                        header_buttons['rawMaterial_'+element] for element in FORM_HEADER_DICT['sample']['rawMaterial'].keys()
                                    ],
                                    title="Raw Material (soil, water, gas, etc.)",
                                ),
                            ],
                            start_collapsed=True
                        ),                      
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
                    width=4
                ),
                dbc.Col(
                    children=[
                        html.H3('Study Types'),
                        html.Br(),
                        dbc.Accordion(
                            [
                                dbc.AccordionItem(
                                    [
                                        # html.Div(dbc.Button(element,id=element),style={'padding':5}) for element in FORM_HEADER_DICT['study']['genetic'].keys()
                                        header_buttons['genetic_'+element] for element in FORM_HEADER_DICT['study']['genetic'].keys()
                                    ],
                                    title="Genetic (knockout)",
                                ),
                                dbc.AccordionItem(
                                    [
                                        # dbc.Button(element,id=element) for element in FORM_HEADER_DICT['study']['longitudinal'].keys()
                                        header_buttons['longitudinal_'+element] for element in FORM_HEADER_DICT['study']['longitudinal'].keys()
                                    ],
                                    title="Time Series (longitudinal)",
                                ),
                                dbc.AccordionItem(
                                    [
                                        # dbc.Button(element,id=element) for element in FORM_HEADER_DICT['study']['intervention'].keys()
                                        header_buttons['intervention_'+element] for element in FORM_HEADER_DICT['study']['intervention'].keys()
                                    ],
                                    title="Intervention (drug, diet, exercise, etc.)",
                                ),
                                dbc.AccordionItem(
                                    [
                                        # dbc.Button(element,id=element) for element in FORM_HEADER_DICT['study']['effect'].keys()
                                        header_buttons['effect_'+element] for element in FORM_HEADER_DICT['study']['effect'].keys()
                                    ],
                                    title="Effect (disease, etc.)",
                                ),
                            ],
                            start_collapsed=True
                        ),  
                        # dbc.Checklist(
                        #     options=[
                        #         {"label": "Genetic (knockout, CRISPR, MIR, etc.)", "value": 'genetic'},
                        #         {"label": "Time Series (longitudinal)", "value": 'longitudinal'},
                        #         {"label": "Intervention (drug, diet, exercise, etc.)", "value": 'intervention'},
                        #         {"label": "Effect (disease, etc.)", "value": 'effect'},
                        #     ],
                        #     id="study_checklist",
                        # ),
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
        # dbc.Row(
        #     children=[
        #         dbc.Col(width=5),
        #         dbc.Col(
        #             children=[
        #                 html.Div(id='div_filename')
        #             ],
        #             width=2
        #         ),
        #         dbc.Col(width=5)
        #     ]
        # ),
        # html.Br(),
        # html.Br(),
        html.Div(id='Div_curate_button_or_error_messages'),
        
            
    ],
)


@callback(
    [
        Output(component_id="Div_metadata_datatable",component_property="children"),
        #Output(component_id="column_store", component_property="data"),
        # Output(component_id="main_store",component_property="data"),
        # Output(component_id="Div_curate_button_or_error_messages",component_property="children"),
    ],
    [
        #Input(component_id=element, component_property="n_clicks") for element in header_button_names
        Input({'type':'header_button','index':ALL},"n_clicks")
    ],
    [
        #State(component_id="column_store", component_property="data"),
        State(component_id="dt_for_preview",component_property="columns")
    ],
    prevent_initial_call=True
)
def add_column_to_dt(
    header_button_n_clicks,
    dt_for_preview_columns
):
    '''
    basically, we want the state to actually be the DT columns
    read the dt columns, add a new one if the button is clicked
    use the suppress callback thing in the initial case when the dt doesnt exist
    '''
    # print(column_store_data)
    # if column_store_data==None:
    #     column_store_data=list()

    column_type=ctx.triggered_id['index'].split('_')[1]
    columns_to_append=header_button_column_relationships[column_type]

    #column_store_data.append(columns_to_append)
    # column_path=Patch()
    # column_patch
    #print(ctx.triggered_id)

    if dt_for_preview_columns != None:
        total_columns=[
                {'name':temp_element['name'], 'id':temp_element['id']} for temp_element in dt_for_preview_columns
            ]+[
                {'name':temp_element, 'id':temp_element+'-'+str(randint(0,2000000000))} for temp_element in columns_to_append
            ]
    else:
        total_columns=[
                {'name':temp_element, 'id':temp_element+'-'+str(randint(0,2000000000))} for temp_element in columns_to_append
            ]

    print(total_columns)
    total_data=list()
    print(
        {
            temp_col['id']:'download this table' for temp_col in total_columns
        }
    )
    total_data.append(
        {
            temp_col['id']:'download this table' for temp_col in total_columns
        }
    )

    output_children=dbc.Row(
        children=[
            dbc.Col(width=1),
            dbc.Col(
                children=[
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
                ],
                width=10
            ),
            dbc.Col(width=1)
        ]
    ),


    #print(column_store_data)
    return [output_children]
    

# dash_table.DataTable(
#     columns=[
#         {"name": ["", "Year"], "id": "year"},
#         {"name": ["City", "Montreal"], "id": "montreal","deletable":True},
#         {"name": ["City", "Toronto"], "id": "toronto"},
#         {"name": ["City", "Ottawa"], "id": "ottawa"},
#         {"name": ["City", "Vancouver"], "id": "vancouver"},
#         {"name": ["Climate", "Temperature"], "id": "temp"},
#         {"name": ["Climate", "Humidity"], "id": "humidity"},
#     ],
#     data=[
#         {
#             "year": i,
#             "montreal": i * 10,
#             "toronto": i * 100,
#             "ottawa": i * -1,
#             "vancouver": i * -10,
#             "temp": i * -100,
#             "humidity": i * 5,
#         }
#         for i in range(10)
#     ],
#     merge_duplicate_headers=True,


# def generate_header_colors(selected_archetypes,total_headers):
#     '''
#     this generates the dictionaries that are used to color the top row in the excel file
#     we use "groups" as the keys for these because sets of headers arent valid as keys in python
#     '''

#     header_to_archetype_dict=dict()
#     for header in total_headers:
#         #we make sets in each iteration to preserve the order of the list
#         header_to_archetype_dict[header]=FORM_HEADER_DICT_REVERSE[header].intersection(set(selected_archetypes))
    
#     #now we have {header:{archetypes}} for each header
#     #we want to group these sets (we want the reverse of this {{archetypes}:header})
#     #but we cannot use sets as keys
#     #so we settle for a scheme
#     #{group_number:[headers]}
#     #combined with
#     #{group_number:[archetypes]}
#     #first we get the group number keys
#     #this is a list of archtypes [archetypes]
#     unique_groups=[]
#     for header in header_to_archetype_dict.keys():
#         #if the archetype set is not in unique groups
#         if header_to_archetype_dict[header] not in unique_groups:
#             unique_groups.append(header_to_archetype_dict[header])

#     #now for each unique group, get the list of headers associated
#     group_to_header_dict={i:list() for i in range(len(unique_groups))}
#     for temp_header in header_to_archetype_dict:
#         temp_group_number=unique_groups.index(header_to_archetype_dict[temp_header])
#         group_to_header_dict[temp_group_number].append(temp_header)
#     #{group_number:[archetypes]} is the same thing as the unique groups list
#     group_to_archetype_dict={i:element for i,element in enumerate(unique_groups)}

#     return group_to_header_dict,group_to_archetype_dict

def update_excel_sheet_sample_formatting(workbook,worksheet,temp_dataframe):#,group_to_header_dict,group_to_archetype_dict):

    merge_format_dict=dict()

    # #not exactly correct. goal is to strip number from column name
    # #worksheet.max_column
    # for col_num in range(worksheet.dim_colmax + 1):
    #     column = worksheet.col(col_num)
    #     for cell in column:
    #         cell.value = ''.join(filter(str.isalpha, str(cell.value)))
    my_format=workbook.add_format({
        'bold': 1,
        'align': 'center',
        'valign': 'vcenter',
        'font_size':8
    })
    print(worksheet)

    for i,temp_col in enumerate(temp_dataframe.columns):
        proper_text=temp_col.split('-')[0]
        worksheet.write(0,i,proper_text,my_format)


    worksheet.autofit()
    #for temp_col in worksheet.iter_cols(min_row=0,max_row=0,max_col=worksheet.max_column):
    #for col_num in range(worksheet.dim_colmax+1):
        #if temp_col[0].internal_value != None:
        #print('-------------')
        #print(temp_col)
        # proper_text=worksheet.cell_value(0, col_num).split('-')[0]
        # worksheet.write(0,col_num,proper_text,my_format)
        #print(proper_text)
        #cell_location=xl_rowcol_to_cell(temp_col[0])
        # print(cell_location)
        # print(current_internal_text)   
        # c
        # start_cell_xl=xl_rowcol_to_cell(0,start_cell)
        #     end_cell_xl=xl_rowcol_to_cell(0,end_cell)
        #     start_cell=start_cell+len(group_to_header_dict[group_id])
        #     non_merge_string='Associated with: '+(', '.join(group_to_archetype_dict[group_id]))
        #     worksheet.write(start_cell_xl,non_merge_string,merge_format_dict[group_id])


    # for group_id in group_to_header_dict.keys():
    #     merge_format_dict[group_id]=workbook.add_format(
    #         {
    #             'align': 'center',
    #             'valign': 'vcenter',
    #             'fg_color': COLOR_LIST[group_id]
    #         }
    #     )
    # start_cell=0
    # for group_id in merge_format_dict.keys():
    #     end_cell=start_cell+len(group_to_header_dict[group_id])-1
    #     if (end_cell-start_cell)>=1:
    #         start_cell_xl=xl_rowcol_to_cell(0,start_cell)
    #         end_cell_xl=xl_rowcol_to_cell(0,end_cell)
    #         start_cell=start_cell+len(group_to_header_dict[group_id])
    #         merge_string='Associated with: '+(', '.join(group_to_archetype_dict[group_id]))
    #         worksheet.merge_range(
    #             start_cell_xl+':'+end_cell_xl,
    #             merge_string,
    #             merge_format_dict[group_id]
    #         )
    #     elif (end_cell-start_cell)==0:
    #         start_cell_xl=xl_rowcol_to_cell(0,start_cell)
    #         end_cell_xl=xl_rowcol_to_cell(0,end_cell)
    #         start_cell=start_cell+len(group_to_header_dict[group_id])
    #         non_merge_string='Associated with: '+(', '.join(group_to_archetype_dict[group_id]))
    #         worksheet.write(start_cell_xl,non_merge_string,merge_format_dict[group_id])
    worksheet.autofit()

    return workbook, worksheet

def fill_title_sheet(temp_writer,workbook,worksheet):
    worksheet=temp_writer.sheets['title_page']
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


# def generate_curated_colors(worksheet,dataframe):
#     '''

#     '''

#     max_col=worksheet.max_column

#     #find the furthest left archetype that has text
#     for temp_col in worksheet.iter_cols(min_row=1,max_row=1,max_col=max_col):
#         if temp_col[0].internal_value != None:
#             current_internal_text=temp_col[0].internal_value
#             break
            
#     group_to_header_dict=dict()
#     group_to_text_dict=dict()        
#     current_group=0
#     group_to_header_dict[current_group]=set()
#     group_to_text_dict[current_group]=current_internal_text

#     for temp_col in worksheet.iter_cols(min_row=1,max_row=2,max_col=max_col):
#         try:
#             if (temp_col[0].internal_value == current_internal_text) or (temp_col[0].internal_value is None):
#                 group_to_header_dict[current_group].add(
#                     temp_col[1].internal_value
#                 )
#             else:
#                 current_group+=1
#                 current_internal_text=temp_col[0].internal_value
#                 group_to_text_dict[current_group]=current_internal_text
#                 group_to_header_dict[current_group]={temp_col[1].internal_value}
#         except AttributeError:
#             group_to_header_dict[current_group].add(
#                 temp_col[1].internal_value
#             )

#     #convert to list so that we can use the dash object store, which has json rules
#     for item in group_to_header_dict.keys():
#         group_to_header_dict[item]=list(group_to_header_dict[item])

#     return group_to_header_dict,group_to_text_dict


@callback(
    [
        Output(component_id="upload_form",component_property="children"),
        Output(component_id="main_store",component_property="data"),
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
        header_button_column_relationships
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
                            )
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

            store_dict={
                'input_dataframe':temp_dataframe_as_json,
            }

    displayed_name=html.Div([upload_form_filename],className='text-center')
    return [displayed_name,store_dict,curate_button_children]





