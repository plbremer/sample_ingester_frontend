import dash
from dash import dcc, html,dash_table,callback, ctx
import plotly.express as px
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State

from dash.exceptions import PreventUpdate

from nltk.util import trigrams
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors
import json
import os
import time
import pickle
import pandas as pd

from pprint import pprint


nearest_neighbors_model_address='additional_files/NearestNeighbors.bin'
tfidf_vectorizer_model_address='additional_files/tfidfVectorizer.bin'
valid_string_as_key_json_address='additional_files/combined_valid_string_as_key.json'
valid_string_list_dataframe_address='additional_files/valid_string_list_dataframe.bin'

with open(nearest_neighbors_model_address, 'rb') as f: 
    nearest_neighbors_model=pickle.load(f)
with open(tfidf_vectorizer_model_address, 'rb') as f:
    tfidf_vectorizer_model=pickle.load(f)
valid_string_list_dataframe=pd.read_pickle(valid_string_list_dataframe_address)
valid_string_list_array=valid_string_list_dataframe['valid_strings'].values
with open(valid_string_as_key_json_address, 'r') as f:
    valid_string_as_key_json=json.load(f)

# def curate_data(
#     main_store_data
# ):

#     #print(ctx.triggered_id)
#     print(main_store_data)

#     print('hi')
#     return ['hji']


def parse_excel_file(store_panda):

    output_dict=dict()
    for temp_header in store_panda.columns:
        output_dict[temp_header]=store_panda[temp_header].unique().tolist()
    return output_dict
    
def find_neighbors_per_string(written_strings_per_category):
    '''
    receives

    {0: ['human', 'Humen'], 1: ['serum'], 2: [10, 11, 12]}
    '''
    
    output_dict=dict()

    #we can upgrade the vectorization to a, no pun intended, vectorized way, later
    for temp_header in written_strings_per_category.keys():
        output_dict[temp_header]=dict()
        for temp_written_string in written_strings_per_category[temp_header]:
            #vectorizer expects iterable. wrap in list to achieve
            #FIX: atm we typecase ints to strings
            vectorized_string=tfidf_vectorizer_model.transform([str(temp_written_string)])
            #kn_ind is an array of indices of the nieghbors in the training matrix
            _,kn_ind=nearest_neighbors_model.kneighbors(
                vectorized_string,
                5
                )
            #[0] because the shape of the array is array([[842652, 842654, 842651, 842649, 842653]]
            output_dict[temp_header][temp_written_string]=valid_string_list_array[kn_ind[0]]

            
    return output_dict


def generate_dropdown_options(valid_string_neighbors):
    '''
    receives 

    {0: {'Humen': array(['Humerus', 'Humerana', 'ume', 'Rumen', 'Cerumen'], dtype=object),
        'human': array(['human', 'humans', 'Schumannia', 'human lice', 'Schumannella'],
        dtype=object)},
    1: {'serum': array(['Serum', 'Verum', 'Noserus', 'Cerumen', 'Sclerum'], dtype=object)},
    2: {10: array(['Ablabys taenianotus', 'Sillaginopsis domina', 'cockatoo waspfish',
        'Synodus fuscus', 'Taeniamia dispilus'], dtype=object),
        11: array(['Ablabys taenianotus', 'Sillaginopsis domina', 'cockatoo waspfish',
        'Synodus fuscus', 'Taeniamia dispilus'], dtype=object),
        12: array(['Ablabys taenianotus', 'Sillaginopsis domina', 'cockatoo waspfish',
        'Synodus fuscus', 'Taeniamia dispilus'], dtype=object)}}    
    '''
    output_dict=dict()
    for temp_header in valid_string_neighbors.keys():
        output_dict[temp_header]=dict()

        for temp_written_string in valid_string_neighbors[temp_header].keys():
            output_dict[temp_header][temp_written_string]=list()

            for temp_valid_string in valid_string_neighbors[temp_header][temp_written_string]:

                temp_relevant_nodes_list=valid_string_as_key_json[temp_valid_string]
                #we have to do this extra one because in a few cases there is more than one node for a valid string
                for temp_relevant_node in temp_relevant_nodes_list:

                    output_dict[temp_header][temp_written_string].append(
                        {
                            'label':temp_valid_string+' AKA '+temp_relevant_node['main_string']+' NODE '+temp_relevant_node['node_id'],
                            'value':temp_valid_string+' AKA '+temp_relevant_node['main_string']+' NODE '+temp_relevant_node['node_id']
                        }
                    )
                    
    return output_dict

def generate_input_to_dropdown_column_for_datatable(dropdown_options):
    '''
    receives

    {0: {'Humen': [{'label': 'Humerus AKA Humerus',
                    'value': 'Humerus AKA Humerus NODE '
                            'mesh_A02.835.232.087.090.400'},
                {'label': 'Humerana AKA Humerana',
                    'value': 'Humerana AKA Humerana NODE ncbi_1659744'},
                {'label': 'ume AKA Prunus mume',
                    'value': 'ume AKA Prunus mume NODE ncbi_102107'},
                {'label': 'Rumen AKA Rumen',
                    'value': 'Rumen AKA Rumen NODE mesh_A13.869.804'},
                {'label': 'Cerumen AKA Cerumen',
                    'value': 'Cerumen AKA Cerumen NODE mesh_A12.200.147'}],
        'human': [{'label': 'human AKA Homo sapiens',
                    'value': 'human AKA Homo sapiens NODE ncbi_9606'},
                {'label': 'humans AKA Homo',
                    'value': 'humans AKA Homo NODE ncbi_9605'},
                {'label': 'Schumannia AKA Schumannia',
                    'value': 'Schumannia AKA Schumannia NODE ncbi_489378'},
                {'label': 'human lice AKA Pediculus humanus',
                    'value': 'human lice AKA Pediculus humanus NODE ncbi_121225'},
                {'label': 'Schumannella AKA Schumannella',
                    'value': 'Schumannella AKA Schumannella NODE ncbi_472058'}]},
    1: {'serum': [{'label': 'Serum AKA Serum',    

    want
    [
        {
            'options':{
                'label':
                'value'
            }
        },
        {
            'options':{
                'label':
                'value'
            }
        }
    ]

    1/2 helpers taht ultimatley didnt work. combined into "generate_datatable_records"
    '''

    output_list=list()

    for temp_header in dropdown_options.keys():
        for temp_written_string in dropdown_options[temp_header].keys():
            
            #print(dropdown_options[temp_header][temp_written_string])
            #hold=input('&^%*(&^)(*&)(_*&)(*&^*(&^(*&^(*)&')



            output_list.append(
                {
                    
                    'alternative_guesses':{
                        'options':dropdown_options[temp_header][temp_written_string],
                        #'placeholder':'hi'
                    }
                    
                }
            )

    return output_list

def generate_input_to_other_columns_for_datatable(dropdown_options):
    '''
    #2/2 helpers taht ultimatley didnt work. combined into "generate_datatable_records"
    '''
    
    output_dict={
        "header_type":[],
        "value_parsed":[],
        "best_guess":[],
        #"alternative_guesses":['hi'],
        "free_text":[]
    }       

    for temp_header in dropdown_options.keys():
        for temp_written_string in dropdown_options[temp_header].keys():
            output_dict['header_type'].append(temp_header)
            output_dict['best_guess'].append(dropdown_options[temp_header][temp_written_string][0]['value'])
            output_dict['value_parsed'].append(temp_written_string)
            output_dict['free_text'].append('')

    return output_dict





def generate_datatable_records(dropdown_options):


    output_list=list()

    for temp_header in dropdown_options.keys():
        for temp_written_string in dropdown_options[temp_header].keys():
            output_list.append(
                {
                    "header_type":temp_header,
                    "value_parsed":temp_written_string,
                    "best_guess":dropdown_options[temp_header][temp_written_string][0]['value'],
                    #"alternative_guesses":'hi',
                    "free_text":'',
                    'alternative_guesses':{
                        'options':{
                            dropdown_options[temp_header][temp_written_string]
                        }
                    }
                }              
            )

            
            
            
            
            # output_list.append(
            #     {
            #         'options':{
            #             dropdown_options[temp_header][temp_written_string]
            #         }
            #     }
            # )

    return output_list






dash.register_page(__name__, path='/curate-and-download')

layout = html.Div(
    children=[
        # dcc.Interval(
        #     id="load_interval", 
        #     interval=0,
        #     n_intervals=0, 
        #     max_intervals=0, 
        # ),
        
        html.Br(),
        html.Br(),
        dbc.Row(
            children=[
                dbc.Col(width=1),
                dbc.Col(
                    children=[


                        dash_table.DataTable(
                            id='table_curation',
                            editable=True,
                            columns=[
                                {"name": "header_type", "id": "header_type"},
                                {"name": "value_parsed", "id": "value_parsed"},
                                {"name": "best_guess", "id": "best_guess"},
                                {"name": "alternative_guesses", "id": "alternative_guesses","presentation": "dropdown"},
                                {"name": "free_text", "id": "free_text"},
                            ],
                            #data=[{'header_type': 0, 'value_parsed': 'human', 'best_guess': 'human AKA Homo sapiens NODE ncbi_9606', 'free_text': ''}, {'header_type': 0, 'value_parsed': 'Humen', 'best_guess': 'Humerus AKA Humerus NODE mesh_A02.835.232.087.090.400', 'free_text': ''}, {'header_type': 1, 'value_parsed': 'serum', 'best_guess': 'Serum AKA Serum NODE mesh_A12.207.152.846', 'free_text': ''}, {'header_type': 2, 'value_parsed': 10, 'best_guess': 'Ablabys taenianotus AKA Ablabys taenianotus NODE ncbi_1604563', 'free_text': ''}, {'header_type': 2, 'value_parsed': 11, 'best_guess': 'Ablabys taenianotus AKA Ablabys taenianotus NODE ncbi_1604563', 'free_text': ''}, {'header_type': 2, 'value_parsed': 12, 'best_guess': 'Ablabys taenianotus AKA Ablabys taenianotus NODE ncbi_1604563', 'free_text': ''}],
                            #dropdown_data=[{'alternative_guesses': {'options': [{'label': 'hi', 'value': 'hi'}]}},                            {'alternative_guesses': {'options': [{'label': 'hi', 'value': 'hi'}]}},                            {'alternative_guesses': {'options': [{'label': 'hi', 'value': 'hi'}]}},                            {'alternative_guesses': {'options': [{'label': 'hi', 'value': 'hi'}]}},                            {'alternative_guesses': {'options': [{'label': 'hi', 'value': 'hi'}]}},                            {'alternative_guesses': {'options': [{'label': 'hi', 'value': 'hi'}]}}],
                            data=[],
                            dropdown_data=[],
                            # data=curate_data(
                            #     State(component_id="main_store",component_property="data")
                            # ),
                            #page_current=0,  
                            #for whatever reason, case insensitive breaks the magnitude filter                              
                            # filter_options={
                            #     'case':'insensitive',
                            #     'placeholder_text':'Type here to filter'
                            # },
                            page_size=50,
                            page_action='native',
                            sort_action='native',
                            sort_mode='multi',
                            #filter_action='native',
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
                            css=[ {"selector": ".Select-menu-outer", "rule": 'display : block !important'} ]
                        )






                    ],
                    width=4
                ),
                dbc.Col(
                    # children=[
                    #     html.H3('Study Descriptors'),
                    # ],
                    width=4
                ),
                dbc.Col(width=2)
            ]
        )
    ],
)


@callback(
    [
        #Output(component_id="here_is_where_we_put_the curation_interface", component_property="children"),
        Output(component_id="table_curation", component_property="data"),
        Output(component_id="table_curation", component_property="dropdown_data"),
        #Output(component_id="main_store",component_property="data")
    ],
    [
        #Input(component_id="upload_form", component_property="contents"),
        #Input(component_id="load_interval", component_property="n_intervals")
        Input(component_id="url", component_property="href")
    ],
    [
        #State(component_id="upload_form", component_property="filename"),
        State(component_id="main_store",component_property="data"),
    ],
    #prevent_initial_call=True
)
def curate_data(
    #load_interval_n_intervals,
    url_href,
    main_store_data
):
    print('==========================================')
    #print(ctx.triggered_id)
    #print(load_interval_n_intervals)
    url_href_page_location=url_href.split('/')[-1]
    #print(url_href)
    if url_href_page_location!='curate-and-download':
        raise PreventUpdate

    #total hack. could not get component to behave as expectred. n_intervals was 1 then 0 then 1
    # if load_interval_n_intervals!=0:
    #     raise PreventUpdate

    print(main_store_data)

    store_panda=pd.DataFrame.from_records(main_store_data)
    print(store_panda)


    written_strings_per_category=parse_excel_file(store_panda)
    print(written_strings_per_category)

    valid_string_neighbors=find_neighbors_per_string(written_strings_per_category)
    pprint(valid_string_neighbors)

    dropdown_options=generate_dropdown_options(valid_string_neighbors)
    # pprint(dropdown_options)

    #ultimatley, there is a rwo for every written component
    curation_datatable_data=generate_input_to_other_columns_for_datatable(dropdown_options)
    temp_panda=pd.DataFrame.from_dict(curation_datatable_data)
    # print(test_panda)
    # print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
    curation_datatable_data_records=temp_panda.to_dict(orient='records')
    
    print(curation_datatable_data_records)
    
    
    curation_datatable_dropdowns=generate_input_to_dropdown_column_for_datatable(dropdown_options)
    # curation_datatable_dropdowns=[
    #     {
    #         'alternative_guesses':{
    #             'options':[
    #                 {
    #                     'label':'hi',
    #                     'value':'hi'
    #                 }
    #             ]
    #         }
    #     }
    #     for i in curation_datatable_data_records
    # ]
    
    #curation_data['alternative_guesses']=dropdown_options

    #output_data_records_format=generate_datatable_records(dropdown_options)



    pprint(curation_datatable_dropdowns)


    return [curation_datatable_data_records,curation_datatable_dropdowns]











# from collections import OrderedDict

# # We will cover all 3 DataTable Dropdown options:
# # 1. per-Column Dropdowns (you choose column)
# # 2. per-Row Dropdowns (starts from 1st row to as many rows as you want)
# # 3. per-Row-Col Dropdowns (conditional, you choose which row/column)
# #-----------------------------------
# # 1. DataTable with Per-Column Dropdowns

# df = pd.DataFrame(OrderedDict([
#     ('climate', ['Sunny', 'Snowy', 'Sunny', 'Rainy']),
#     ('temperature', [13, 43, 50, 30]),
#     ('city', ['NYC', 'Montreal', 'Miami', 'NYC'])
# ]))


# layout = html.Div([
#     dash_table.DataTable(
#         id='table-dropdown',
#         data=df.to_dict('records'),
#         columns=[
#             {'id': 'climate', 'name': 'climate', 'presentation': 'dropdown'},
#             {'id': 'temperature', 'name': 'temperature'},
#             {'id': 'city', 'name': 'city', 'presentation': 'dropdown'},
#         ],
#         editable=True,
#                                         #list of dictionaries. One dict per row
#         dropdown_data=[{                #their keys represent column IDs
#             'climate': {                #their values are 'options' and 'clearable'
#                 'options': [            #'options' represent cell data
#                     {'label': i, 'value': i}
#                     for i in df['climate'].unique()
#                 ],

#                 'clearable':True
#             },

#             'city': {
#                 'options': [
#                     {'label': i, 'value': i}
#                     for i in df['city'].unique()
#                 ],

#                 'clearable':True
#             },
#         } for x in range(2)
#         ],
#         css=[ {"selector": ".Select-menu-outer", "rule": 'display : block !important'} ]

#     ),
# ])


