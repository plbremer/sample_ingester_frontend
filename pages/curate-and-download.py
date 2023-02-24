from re import T
import dash
from dash import dcc, html,dash_table,callback, ctx,MATCH
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



#get the headers and their subset definitions
with open('additional_files/subset_per_heading.json', 'r') as fp:
    subset_per_heading_json=json.load(fp)

#get all of the models
nearest_neighbors_dict=dict()
tfidf_vectorizer_dict=dict()
model_files=os.listdir('additional_files/')
for temp_file_name in model_files:
    temp_header=temp_file_name.split('.')[0].split('_')[-1]
    if 'NearestNeighbors' in temp_file_name:
        with open(f'additional_files/{temp_file_name}', 'rb') as f:
            nearest_neighbors_dict[temp_header]=pickle.load(f)
    elif 'tfidfVectorizer' in temp_file_name:
        with open(f'additional_files/{temp_file_name}', 'rb') as f:
            tfidf_vectorizer_dict[temp_header]=pickle.load(f)


#get all of the vocabulary dicts
conglomerate_vocabulary_panda_dict=dict()
for temp_file_name in model_files:
    temp_header=temp_file_name.split('.')[0].split('_')[-1]
    if 'conglomerate_vocabulary_panda' in temp_file_name:
        temp_panda=pd.read_pickle(f'additional_files/{temp_file_name}')
        #temp panda has header 0 not "valid string unique" for some reason
        conglomerate_vocabulary_panda_dict[temp_header]=temp_panda
        #vocabulary_dict[temp_header]=temp_panda[0].values
#print(conglomerate_vocabulary_panda_dict.keys())
#its_ya_boy=input('key check')



#conglomerate_vocabulary_panda=pd.read_pickle('additional_files/conglomerate_vocabulary_panda.bin')

# #get a view for each of the temp headers, the same view that was used to make the models
# header_vocabulary_json_address="additional_files/subset_per_heading.json"
# with open(header_vocabulary_json_address,'r') as f:
#     header_vocabulary_json=json.load(f)
# # gui_headers=header_vocabulary_json.keys()

#get the vocaulary for each header. used to infer the valid_string from locattion.
#nearest neighbors model outputs location of match on list.
vocabulary_dict=dict()
for temp_file_name in model_files:
    temp_header=temp_file_name.split('.')[0].split('_')[-1]
    if 'unique_valid_strings' in temp_file_name:
        temp_panda=pd.read_pickle(f'additional_files/{temp_file_name}')
        #temp panda has header 0 not "valid string unique" for some reason
        vocabulary_dict[temp_header]=temp_panda[0].values


# print(tfidf_vectorizer_dict.keys())
# print(tfidf_vectorizer_dict['species'])
# hold=input('key check')
# for temp_header in header_vocabulary_json.keys():
#     temp_subset_definitions=header_vocabulary_json[temp_header]
#     temp_panda_list=list()
#strictly speaking, we should proabbly subset the panda. the reason being that we fcould technically reach out into a region that is unrelated
#like "DDT" has meaning for both chemicals and genes. so we wouldnt want the chemical nodes showing up during a gene search


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

    # temp_nearest_neighbors_dict=dict()
    # temp_tfidf_vectorizer_dict=dict()


    #we can upgrade the vectorization to a, no pun intended, vectorized way, later
    for temp_header in written_strings_per_category.keys():
        
        #we dont curate certain categories esp numerical like height, weight, etc
        if temp_header not in subset_per_heading_json.keys():
            continue
        
        output_dict[temp_header]=dict()
        for temp_written_string in written_strings_per_category[temp_header]:
            #vectorizer expects iterable. wrap in list to achieve
            #FIX: atm we typecase ints to strings
            print('123456789012345678901234567890')
            print(tfidf_vectorizer_dict['species'])
            print(tfidf_vectorizer_dict[temp_header])
            
            #neighbors
            
            vectorized_string=tfidf_vectorizer_dict[temp_header].transform([str(temp_written_string)])
            
            neghbors_to_retrieve=5
            if (nearest_neighbors_dict[temp_header].n_samples_fit_) < neghbors_to_retrieve:
                neghbors_to_retrieve=nearest_neighbors_dict[temp_header].n_samples_fit_

            #kn_ind is an array of indices of the nieghbors in the training matrix
            _,kn_ind=nearest_neighbors_dict[temp_header].kneighbors(
                vectorized_string,
                neghbors_to_retrieve
            )
            #[0] because the shape of the array is array([[842652, 842654, 842651, 842649, 842653]]
            output_dict[temp_header][temp_written_string]=vocabulary_dict[temp_header][kn_ind[0]]
            
    pprint(output_dict)
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


    outputs 
    '''
    output_dict=dict()
    for temp_header in valid_string_neighbors.keys():

        #we dont curate certain categories esp numerical like height, weight, etc
        if temp_header not in subset_per_heading_json.keys():
            continue


        output_dict[temp_header]=dict()

        for temp_written_string in valid_string_neighbors[temp_header].keys():
            output_dict[temp_header][temp_written_string]=list()

            for temp_valid_string in valid_string_neighbors[temp_header][temp_written_string]:

                ###temp_relevant_nodes_list=valid_string_as_key_json[temp_valid_string]
                temp_relevant_nodes_rows=conglomerate_vocabulary_panda_dict[temp_header].loc[
                    conglomerate_vocabulary_panda_dict[temp_header]['valid_string']==temp_valid_string
                ].drop_duplicates(subset=('valid_string','main_string'))
                #we have to do this extra one because in a few cases there is more than one node for a valid string
                #this entire appraoch is proabbly a little dated because we grew to use padnas not jsons but oh well
                ###for temp_relevant_node in temp_relevant_nodes_list:
                
                for index,series in temp_relevant_nodes_rows.iterrows():
                    output_dict[temp_header][temp_written_string].append(
                        {
                            'label':temp_valid_string+' AKA '+series['main_string'],#+' NODE '+series['node_id'],
                            'value':temp_valid_string+' AKA '+series['main_string']#+' NODE '+series['node_id']                
                        }
                    )
                    # output_dict[temp_header][temp_written_string].append(
                    #     {
                    #         'label':temp_valid_string+' AKA '+temp_relevant_node['main_string']+' NODE '+temp_relevant_node['node_id'],
                    #         'value':temp_valid_string+' AKA '+temp_relevant_node['main_string']+' NODE '+temp_relevant_node['node_id']
                    #     }
                    # )
                    
    return output_dict

# def generate_input_to_dropdown_column_for_datatable(dropdown_options):
#     '''
#     receives

#     {0: {'Humen': [{'label': 'Humerus AKA Humerus',
#                     'value': 'Humerus AKA Humerus NODE '
#                             'mesh_A02.835.232.087.090.400'},
#                 {'label': 'Humerana AKA Humerana',
#                     'value': 'Humerana AKA Humerana NODE ncbi_1659744'},
#                 {'label': 'ume AKA Prunus mume',
#                     'value': 'ume AKA Prunus mume NODE ncbi_102107'},
#                 {'label': 'Rumen AKA Rumen',
#                     'value': 'Rumen AKA Rumen NODE mesh_A13.869.804'},
#                 {'label': 'Cerumen AKA Cerumen',
#                     'value': 'Cerumen AKA Cerumen NODE mesh_A12.200.147'}],
#         'human': [{'label': 'human AKA Homo sapiens',
#                     'value': 'human AKA Homo sapiens NODE ncbi_9606'},
#                 {'label': 'humans AKA Homo',
#                     'value': 'humans AKA Homo NODE ncbi_9605'},
#                 {'label': 'Schumannia AKA Schumannia',
#                     'value': 'Schumannia AKA Schumannia NODE ncbi_489378'},
#                 {'label': 'human lice AKA Pediculus humanus',
#                     'value': 'human lice AKA Pediculus humanus NODE ncbi_121225'},
#                 {'label': 'Schumannella AKA Schumannella',
#                     'value': 'Schumannella AKA Schumannella NODE ncbi_472058'}]},
#     1: {'serum': [{'label': 'Serum AKA Serum',    

#     want
#     [
#         {
#             'options':{
#                 'label':
#                 'value'
#             }
#         },
#         {
#             'options':{
#                 'label':
#                 'value'
#             }
#         }
#     ]

#     1/2 helpers taht ultimatley didnt work. combined into "generate_datatable_records"
#     '''

#     output_list=list()

#     for temp_header in dropdown_options.keys():
#         for temp_written_string in dropdown_options[temp_header].keys():
            
#             #print(dropdown_options[temp_header][temp_written_string])
#             #hold=input('&^%*(&^)(*&)(_*&)(*&^*(&^(*&^(*)&')



#             output_list.append(
#                 {
                    
#                     'alternative_guesses':{
#                         'options':dropdown_options[temp_header][temp_written_string],
#                         #'placeholder':'hi'
#                     }
                    
#                 }
#             )

#     return output_list

# def generate_input_to_other_columns_for_datatable(dropdown_options):
#     '''
#     #2/2 helpers taht ultimatley didnt work. combined into "generate_datatable_records"
#     '''
    
#     output_dict={
#         "header_type":[],
#         "value_parsed":[],
#         "best_guess":[],
#         #"alternative_guesses":['hi'],
#         "free_text":[]
#     }       

#     for temp_header in dropdown_options.keys():
#         for temp_written_string in dropdown_options[temp_header].keys():
#             output_dict['header_type'].append(temp_header)
#             output_dict['best_guess'].append(dropdown_options[temp_header][temp_written_string][0]['value'])
#             output_dict['value_parsed'].append(temp_written_string)
#             output_dict['free_text'].append('')

#     return output_dict





# def generate_datatable_records(dropdown_options):


#     output_list=list()

#     for temp_header in dropdown_options.keys():
#         for temp_written_string in dropdown_options[temp_header].keys():
#             output_list.append(
#                 {
#                     "header_type":temp_header,
#                     "value_parsed":temp_written_string,
#                     "best_guess":dropdown_options[temp_header][temp_written_string][0]['value'],
#                     #"alternative_guesses":'hi',
#                     "free_text":'',
#                     'alternative_guesses':{
#                         'options':{
#                             dropdown_options[temp_header][temp_written_string]
#                         }
#                     }
#                 }              
#             )

#     return output_list






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
        # dbc.Row(
        #     children=[
        #         dbc.Col(width=1),
        #         dbc.Col(
        #             children=[


        #                 dash_table.DataTable(
        #                     id='table_curation',
        #                     editable=True,
        #                     columns=[
        #                         {"name": "header_type", "id": "header_type"},
        #                         {"name": "value_parsed", "id": "value_parsed"},
        #                         {"name": "best_guess", "id": "best_guess"},
        #                         {"name": "alternative_guesses", "id": "alternative_guesses","presentation": "dropdown"},
        #                         {"name": "free_text", "id": "free_text"},
        #                     ],
        #                     #data=[{'header_type': 0, 'value_parsed': 'human', 'best_guess': 'human AKA Homo sapiens NODE ncbi_9606', 'free_text': ''}, {'header_type': 0, 'value_parsed': 'Humen', 'best_guess': 'Humerus AKA Humerus NODE mesh_A02.835.232.087.090.400', 'free_text': ''}, {'header_type': 1, 'value_parsed': 'serum', 'best_guess': 'Serum AKA Serum NODE mesh_A12.207.152.846', 'free_text': ''}, {'header_type': 2, 'value_parsed': 10, 'best_guess': 'Ablabys taenianotus AKA Ablabys taenianotus NODE ncbi_1604563', 'free_text': ''}, {'header_type': 2, 'value_parsed': 11, 'best_guess': 'Ablabys taenianotus AKA Ablabys taenianotus NODE ncbi_1604563', 'free_text': ''}, {'header_type': 2, 'value_parsed': 12, 'best_guess': 'Ablabys taenianotus AKA Ablabys taenianotus NODE ncbi_1604563', 'free_text': ''}],
        #                     #dropdown_data=[{'alternative_guesses': {'options': [{'label': 'hi', 'value': 'hi'}]}},                            {'alternative_guesses': {'options': [{'label': 'hi', 'value': 'hi'}]}},                            {'alternative_guesses': {'options': [{'label': 'hi', 'value': 'hi'}]}},                            {'alternative_guesses': {'options': [{'label': 'hi', 'value': 'hi'}]}},                            {'alternative_guesses': {'options': [{'label': 'hi', 'value': 'hi'}]}},                            {'alternative_guesses': {'options': [{'label': 'hi', 'value': 'hi'}]}}],
        #                     data=[],
        #                     dropdown_data=[],
        #                     # data=curate_data(
        #                     #     State(component_id="main_store",component_property="data")
        #                     # ),
        #                     #page_current=0,  
        #                     #for whatever reason, case insensitive breaks the magnitude filter                              
        #                     # filter_options={
        #                     #     'case':'insensitive',
        #                     #     'placeholder_text':'Type here to filter'
        #                     # },
        #                     page_size=50,
        #                     page_action='native',
        #                     sort_action='native',
        #                     sort_mode='multi',
        #                     #filter_action='native',
        #                     style_cell={
        #                         'fontSize': 17,
        #                         'padding': '8px',
        #                         'textAlign': 'center'
        #                     },
        #                     style_header={
        #                         'font-family': 'arial',
        #                         'fontSize': 15,
        #                         'fontWeight': 'bold',
        #                         'textAlign': 'center'
        #                     },
        #                     style_data={
        #                         'textAlign': 'center',
        #                         'fontWeight': 'bold',
        #                         'font-family': 'Roboto',
        #                         'fontSize': 15,
        #                     },
        #                     css=[ {"selector": ".Select-menu-outer", "rule": 'display : block !important'} ]
        #                 )
        #             ],
        #             width=4
        #         ),
        #         dbc.Col(
        #             # children=[
        #             #     html.H3('Study Descriptors'),
        #             # ],
        #             width=4
        #         ),
        #         dbc.Col(width=2)
        #     ]
        # ),

        dbc.Row(
            children=[
                html.Div(
                    id='here_is_where_we_put_the curation_interface'
                )
            ]
        )

    ],
)


@callback(
    [
        Output(component_id="here_is_where_we_put_the curation_interface", component_property="children"),
        #Output(component_id="table_curation", component_property="data"),
        #Output(component_id="table_curation", component_property="dropdown_data"),
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

    store_panda=pd.read_json(main_store_data,orient='records')
    print(store_panda)


    written_strings_per_category=parse_excel_file(store_panda)
    print(written_strings_per_category)

    print('`````````````````````````````````````````````````')

    valid_string_neighbors=find_neighbors_per_string(written_strings_per_category)
    pprint(valid_string_neighbors)

    dropdown_options=generate_dropdown_options(valid_string_neighbors)
    pprint(dropdown_options)


    output_children=list()


    output_children.append(
        dbc.Row(
            children=[
                #dbc.Col(width=1),
                dbc.Col(
                    children=[
                        html.H3('User Entry'),
                        html.Br()                        
                    ]
                ),    
                dbc.Col(
                    html.H3('Best Guess')
                ),
                #the dropdown for strings that are close
                dbc.Col(
                    html.H3('Similar Guesses')
                ),
                #the dropdown with completely empty boxes
                dbc.Col(
                    html.H3('Type to match text')  
                ),

                #the empty input to create your own
                dbc.Col(
                    html.H3('Reject suggestions, create new')
                )

            ]
        )
    )






    
    #there is a row per (temp_header,temp_written_string)
    for temp_header in dropdown_options.keys():
        for temp_written_string in dropdown_options[temp_header].keys():
            output_children.append(
                dbc.Row(
                    children=[
                        #dbc.Col(width=1),
                        dbc.Col(
                            html.H6(str(temp_header)+': '+str(temp_written_string))
                        ),    
                        dbc.Col(
                            html.H6(
                                dropdown_options[temp_header][temp_written_string][0]['label']
                            ),
                        ),
                        #the dropdown for strings that are close
                        dbc.Col(
                            dcc.Dropdown(
                                id={
                                    'type':'dropdown_similar_strings',
                                    'index':str(temp_header)+'_'+str(temp_written_string)
                                },
                                options=[label_value_pair for label_value_pair in dropdown_options[temp_header][temp_written_string]]
                            )
                        ),
                        #the dropdown with completely empty boxes
                        dbc.Col(
                            dcc.Dropdown(
                                id={
                                    'type':'dropdown_empty_options',
                                    'index':str(temp_header)+'_'+str(temp_written_string)
                                },
                                multi=False,
                                placeholder='Type compound name to search',
                                options=['Type substring to populate options.']
                            ),  
                        ),

                        #the empty input to create your own
                        dbc.Col(
                            dcc.Input(
                                id={
                                    'type':'input_curation',
                                    'index':str(temp_header)+'_'+str(temp_written_string)
                                },
                                placeholder="hate all the proposals? enter your own here!"
                            )
                        )

                    ]
                )
            )


    # #ultimatley, there is a rwo for every written component
    # curation_datatable_data=generate_input_to_other_columns_for_datatable(dropdown_options)
    # temp_panda=pd.DataFrame.from_dict(curation_datatable_data)
    # print(temp_panda)
    # print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
    # curation_datatable_data_records=temp_panda.to_dict(orient='records')
    # print(curation_datatable_data_records)
    # curation_datatable_dropdowns=generate_input_to_dropdown_column_for_datatable(dropdown_options)
    # pprint(curation_datatable_dropdowns)


    #return [curation_datatable_data_records,curation_datatable_dropdowns]

    return [output_children]

@callback(
    Output({'type':'dropdown_empty_options','index':MATCH},'options'),
    #Input("dropdown_bin", "search_value")
    Input({'type':'dropdown_empty_options','index':MATCH},'search_value')
)
def update_options(search_value):
    if not search_value:
        raise PreventUpdate

    if len(search_value)<3:
        raise PreventUpdate
    #conglomerate_vocabulary_panda_dict=dict()
    current_index=ctx.triggered_id['index'].split('_')[0]
    #need to access the index
    print(ctx.triggered_id)
    print('y halo thar')
    #valid_string_list_dataframe
    #at the moment we make it so that the list just serves {'value':'valid_string','label':'valid_string'}
    # temp_valid_values=vocabulary_dict[current_index][
    #     vocabulary_dict[current_index].contains(search_value)
    # ]
    temp_valid_values=conglomerate_vocabulary_panda_dict[current_index].loc[
        conglomerate_vocabulary_panda_dict[current_index]['valid_string'].str.contains(search_value)
    ]['valid_string'].tolist()

    #temp_valid_values=np.core.defchararray.find

    return [
        {   #this form does not match the others. the others take the valid string and plug it into the json. "this is an oldier comment? plb after json to pandas"
            'label': temp_string,
            'value': temp_string
        } for temp_string in temp_valid_values
    ]

    #return [o for o in bins_dict if search_value in o["label"]]








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


