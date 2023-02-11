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


nearest_neighbors_model_address='additional_files/NearestNeighbors.bin'
tfidf_vectorizer_model_address='additional_files/tfidfVectorizer.bin'
valid_string_as_key_json_address='additional_files/combined_valid_string_as_key.json'
valid_string_list_dataframe_address='additional_files/valid_string_list_dataframe.bin'

# with open(nearest_neighbors_model_address, 'rb') as f: 
#     nearest_neighbors_model=pickle.load(f)
# with open(tfidf_vectorizer_model_address, 'rb') as f:
#     tfidf_vectorizer_model=pickle.load(f)
# with open(valid_string_as_key_json_address, 'r') as f:
#     valid_string_as_key_json=json.load(f)
# valid_string_list_dataframe=pd.read_pickle(valid_string_list_dataframe_address)



# def curate_data(
#     main_store_data
# ):

#     #print(ctx.triggered_id)
#     print(main_store_data)

#     print('hi')
#     return ['hji']


def parse_excel_file(store_panda):
    






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
                            columns=[
                                {"name": "header_type", "id": "header_type"},
                                {"name": "value_parsed", "id": "value_parsed"},
                                {"name": "best_guess", "id": "best_guess"},
                                {"name": "alternative_guesses", "id": "alternative_guesses"},
                                {"name": "free_text", "id": "free_text"},
                            ],
                            data=[],
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













    test_dict={
        "header_type":['hi'],
        "value_parsed":['hi'],
        "best_guess":['hi'],
        "alternative_guesses":['hi'],
        "free_text":['hi']
    }

    test_panda=pd.DataFrame.from_dict(test_dict)

    test_output=test_panda.to_dict(orient='records')




    print('hi')
    return [test_output]


