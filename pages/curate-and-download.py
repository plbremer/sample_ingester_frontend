import dash
from dash import dcc, html,dash_table,callback, ctx,MATCH,ALL
import plotly.express as px
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import numpy as np
from dash.exceptions import PreventUpdate

from . import newvocabularyuploadchecker

from nltk.util import trigrams
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors
from sklearn.exceptions import NotFittedError
import json
import os
import time
import pickle
import pandas as pd

import base64
import io

from xlsxwriter.utility import xl_rowcol_to_cell

from pprint import pprint

#get the headers and their subset definitions
with open('additional_files/subset_per_heading.json', 'r') as fp:
    subset_per_heading_json=json.load(fp)
#get the headers and their n gram limits
with open('additional_files/ngram_limits_per_heading.json', 'r') as fp:
    ngram_limits_per_heading_json=json.load(fp)
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
#get the vocaulary for each header. used to infer the valid_string from locattion.
#nearest neighbors model outputs location of match on list.
vocabulary_dict=dict()
for temp_file_name in model_files:
    temp_header=temp_file_name.split('.')[0].split('_')[-1]
    if 'unique_valid_strings' in temp_file_name:
        temp_panda=pd.read_pickle(f'additional_files/{temp_file_name}')
        #temp panda has header 0 not "valid string unique" for some reason
        vocabulary_dict[temp_header]=temp_panda[0].values
        #vocabulary_dict[temp_header]=temp_panda
#from lowest priority to highest
#priority list associated with which column takes priority in curation
priority_list=[
    'H6_best_guess_children_ALL',
    'dropdown_similar_strings_value_ALL',
    'dropdown_empty_options_value_ALL',
    'input_curation_value_ALL'
]

HEADERS_WITH_SHORT_NGRAMS={'heightUnit','weightUnit','ageUnit','massUnit','volumeUnit','timeUnit','drugDoseUnit'}
COLOR_LIST=['red','orange','yellow','green','lime','sky','khaki','red','orange','yellow','green','lime','sky','khaki','red','orange','yellow','green','lime','sky','khaki']

#print(tfidf_vectorizer_dict)


def parse_stored_excel_file(store_panda):
    '''
    extracts the {header:[written_string]} relationship
    '''
    output_dict=dict()
    for temp_header in store_panda.columns:
        output_dict[temp_header]=store_panda[temp_header].dropna().unique().tolist()
    return output_dict
    
def find_neighbors_per_string(written_strings_per_category):
    '''
    receives
    {'species': ['human', 'Humen'], 'organ': ['serum'], 'height': [10, 11, 12]}

    output form
    {'organ': {'root': a dataframe with two columns ([similarity_score_0,similarity_score_1,etc],array(['Foot', 'Tooth Root', 'Root, Tooth', 'Roots, Tooth', 'Tooth']),
        dtype=object)},


    where the list contains *valid_strings*
    '''
    output_dict=dict()
    #print(written_strings_per_category)

    for temp_header in written_strings_per_category.keys():
        #print(temp_header)
        #temp_core_vocabulary allows for the processing of multiple of the same header type, like species, species.1, species.2 etc
        #if for example someone had a chimera.
        temp_header_core_vocabulary=temp_header.split('.')[0]

        #we dont curate certain categories esp numerical like height, weight, etc
        #we recombine those at the end of the curate function
        if temp_header_core_vocabulary not in subset_per_heading_json.keys():
            continue
        
        output_dict[temp_header]=dict()
        for temp_written_string in written_strings_per_category[temp_header]:
            #print('\t'+temp_written_string)
            #if the tfidft vectorizer isnt fitted
            #the neighbors isnt fitted either
            #this happens when the vocabulary ingester is just getting started
            try:
                vectorized_string=tfidf_vectorizer_dict[temp_header_core_vocabulary].transform([str(temp_written_string)])
            except NotFittedError:
                # print(output_dict)
                # print('')
                # print(output_dict[temp_header])
                
                output_dict[temp_header][temp_written_string]=pd.DataFrame.from_dict(
                    {
                        'guessed_valid_strings':[None],
                        'guessed_valid_string_distances':[None]
                    }
                )
                
                
                # (
                #     np.array([None],dtype=object),
                #     np.array(['no options available'],dtype=object)
                # )
                continue

            neighbors_to_retrieve=100
            #if there are fewer neighbors to retrieve than we want, set the neighbors to the max available
            if (nearest_neighbors_dict[temp_header_core_vocabulary].n_samples_fit_) < neighbors_to_retrieve:
                neighbors_to_retrieve=nearest_neighbors_dict[temp_header_core_vocabulary].n_samples_fit_

            #kn_ind is an array of indices of the nieghbors in the training matrix
            similarities,kn_ind=nearest_neighbors_dict[temp_header_core_vocabulary].kneighbors(
                vectorized_string,
                neighbors_to_retrieve
            )
            #print(similarities)
            #print(kn_ind[0])
            #print(vocabulary_dict[temp_header_core_vocabulary])
            #print('2345678982345678904356789034567890-4567890-34567892345678982345678904356789034567890-4567890-3456789')
            #ISSUE 33
            # vocabulary_dict[temp_header]=temp_panda[0].values
            # output_dict[temp_header][temp_written_string]=vocabulary_dict[temp_header_core_vocabulary][kn_ind[0]]
            # output_dict[temp_header][temp_written_string]=(
            #     similarities[0],
            #     vocabulary_dict[temp_header_core_vocabulary][0].values[kn_ind[0]]
            # )
            output_dict[temp_header][temp_written_string]=pd.DataFrame.from_dict(
                {
                    'guessed_valid_strings':vocabulary_dict[temp_header_core_vocabulary][kn_ind[0]],
                    'guessed_valid_string_distances':similarities[0]
                }
            )

    return output_dict

def generate_dropdown_options(valid_string_neighbors):
    '''
    receives 

    {'organ': {'root': a dataframe with two columns ([similarity_score_0,similarity_score_1,etc],array(['Foot', 'Tooth Root', 'Root, Tooth', 'Roots, Tooth', 'Tooth']),
        dtype=object)},
 
    outputs

    {'species': {'human': [{'label': 'human AKA Homo sapiens', 'value': 'human AKA Homo sapiens'}, 
    {'label': 'humata', 'value': 'humata AKA Humata'}, {'label': 'humaria', 'value': 'humaria AKA Humaria'}, 
    {'label': 'schumannia', 'value': 'schumannia AKA Schumannia'}, {'label': 'uma', 'value': 'uma AKA Uma'}, 
    {'label': 'rhuma', 'value': 'rhuma AKA Rhuma'}, {'label': 'schumannella', 'value': 'schumannella AKA Schumannella'}, 
    {'label': 'human torovirus', 'value': 'human torovirus AKA Human torovirus'}, {'label': 'thumatha', 'value': 'thumatha AKA Thumatha'}, 
    {'label': 'human spumaretrovirus', 'value': 'human spumaretrovirus AKA Human spumaretrovirus'}, 
    {'label': 'schumannianthus', 'value': 'schumannianthus AKA Schumannianthus'}, {'label': 'neoschumannia', 'value': 'neoschumannia AKA Neoschumannia'}, 
    {'label': 'glossus humanus', 'value': 'glossus humanus AKA Glossus humanus'}, {'label': 'sordaria humana', 'value': 'sordaria humana AKA Sordaria humana'}, 
    {'label': 'fumana', 'value': 'fumana AKA Fumana'}, {'label': 'human cosavirus a', 'value': 'human cosavirus a AKA Human cosavirus A'}, 
    {'label': 'human cosavirus b', 'value': 'human cosavirus b AKA Human cosavirus B'}, {'label': 'human astrovirus 1', 'value': 'human astrovirus 1 AKA Human astrovirus 1'}, 
    {'label': 'human rotavirus c', 'value': 'human rotavirus c AKA Human rotavirus C'}, 
    {'label': 'human rotavirus a', 'value': 'human rotavirus a AKA Human rotavirus A'}], 'humen':

    outputs 
    '''
    output_dict=dict()
    for temp_header in valid_string_neighbors.keys():
        #we dont curate certain categories esp numerical like height, weight, etc
        temp_header_core_vocabulary=temp_header.split('.')[0]
        
        #i think that this is no longer needed as we filtered in the previous method?
        if temp_header_core_vocabulary not in subset_per_heading_json.keys():
            continue

        output_dict[temp_header]=dict()

        for temp_written_string in valid_string_neighbors[temp_header].keys():
            output_dict[temp_header][temp_written_string]=list()
            



            #originally we had a for loop, but the problem with that was taht was that we were getting a result for each 
            #valid string that the written string mapped to. this meant that we coudl get the same main strin multiple times.
            # temp_relevant_nodes_rows=conglomerate_vocabulary_panda_dict[temp_header_core_vocabulary].loc[
            #     #i think isin is the wrong choice here? i think it should be equal?
            #     #is in is fine... just ahve to reorder
            #     #conglomerate_vocabulary_panda_dict[temp_header]['valid_string'].isin(valid_string_neighbors[temp_header][temp_written_string])
            #     conglomerate_vocabulary_panda_dict[temp_header_core_vocabulary]['valid_string'].isin(valid_string_neighbors[temp_header][temp_written_string])
            # ]
            #print(conglomerate_vocabulary_panda_dict[temp_header_core_vocabulary])

            temp_relevant_nodes_rows=valid_string_neighbors[temp_header][temp_written_string].merge(
                conglomerate_vocabulary_panda_dict[temp_header_core_vocabulary],
                how='left',
                left_on='guessed_valid_strings',
                right_on='valid_string'
            ).drop_duplicates(subset=('main_string')).sort_values(by=['use_count','guessed_valid_string_distances'],ascending=False)

            # temp_concatenated=pd.concat(

            # )
            
            
            # #this is where things are getting rearranged. 
            # #just checking if it is in a list is obliterating the order of the list that we are using to check
            # #instead what we want to do is then for each value, sort
            # #eventually we might want some kind of hybrid function that takes a balance of cosine similarity and use_count
            # #ok so, for the moment, we do not sort by use_count, instead only by cosine score
            # #
            # temp_relevant_nodes_rows['valid_string']=pd.Categorical(
            #     temp_relevant_nodes_rows['valid_string'],
            #     categories=valid_string_neighbors[temp_header][temp_written_string]
            # )
            #temp_relevant_nodes_rows=temp_relevant_nodes_rows.sort_values('valid_string')

            #ISSUE 24
            #we add this condition as the partner condition to the tfidf is fitted check
            #if there are no nodes in the conglomerate panda, then provide these options as a null
            if (len(temp_relevant_nodes_rows.index)==0) or (temp_relevant_nodes_rows.applymap(pd.isnull).all().all() == True):
                output_dict[temp_header][temp_written_string].append(
                        {
                            'label':'no options available',
                            'value':'no options available'
                        }
                    )
                continue
                
            for index,series in temp_relevant_nodes_rows.iterrows():
                #in each of the options, having "thing AKA thing" is 
                #print(series)
                if series['valid_string']==series['main_string'].lower():            
                    output_dict[temp_header][temp_written_string].append(
                        {
                            'label':series['valid_string'],#+' NODE '+series['node_id'],
                            'value':series['valid_string']+' AKA '+series['main_string']                
                        }
                    )
                else:
                    output_dict[temp_header][temp_written_string].append(
                        {
                            'label':series['valid_string']+' AKA '+series['main_string'],#+' NODE '+series['node_id'],
                            'value':series['valid_string']+' AKA '+series['main_string']#+' NODE '+series['node_id']                
                        }
                    )
     
    return output_dict


dash.register_page(__name__, path='/curate-and-download')

layout = html.Div(
    children=[
        dcc.Download(id="download_curated_form"),
        html.Br(),
        html.Br(),
        dbc.Row(
            children=[
                html.Div(
                    id='here_is_where_we_put_the curation_interface'
                )
            ]
        ),
        html.Br(),
        html.Br(),
        dbc.Row(
            children=[
                html.Div(
                    dbc.Button(
                        'Download Curated Form',
                        id='button_download_curated',
                    ),
                    className="d-grid gap-2 col-6 mx-auto",
                ),
            ]
        ),
        html.Br(),
        html.Br(),
        html.Div(id='Div_new_vocab_error_messages'),
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
    '''
    '''
    # print('================================')
    # print('top of curate_data')

    #print('in curate_data')
    url_href_page_location=url_href.split('/')[-1]
    if url_href_page_location!='curate-and-download':
        raise PreventUpdate

    store_panda=pd.read_json(main_store_data['input_dataframe'],orient='records')
    # print(store_panda)
    # print('================================')
    store_panda=store_panda.iloc[:-1,:]

    written_strings_per_category=parse_stored_excel_file(store_panda)
    # print(written_strings_per_category)
    # print('================================')

    #the values come from here sorted by nearest neighbors similarity
    valid_string_neighbors=find_neighbors_per_string(written_strings_per_category)
    # print(valid_string_neighbors)
    # print('================================')

    #if we wanted to implement some sort of use_count + cosine hybrid, this might be the place to do it?
    #we would probably have to pass the cosine scores
    dropdown_options=generate_dropdown_options(valid_string_neighbors)
    # print(dropdown_options)


    output_children=list()


    output_children.append(
        dbc.Row(
            children=[
                dbc.Col(
                    children=[
                        html.H3('User Entry'),
                        html.Br()                        
                    ]
                ),    
                dbc.Col(
                    html.H3('Best Guess')
                ),
                dbc.Col(
                    html.H3('Similar Guesses')
                ),
                dbc.Col(
                    html.H3('Type to match text')  
                ),
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
                            html.H6(
                                id={
                                    'type':'header_written_pair',
                                    'index':str(temp_header)+'_'+str(temp_written_string)
                                },
                                children=[
                                    str(temp_header).split('.')[0]+': '+str(temp_written_string)
                                    #str(temp_header)+': '+str(temp_written_string)
                                ]
                            )
                        ),    
                        dbc.Col(
                            html.H6(
                                id={
                                    'type':'H6_best_guess',
                                    'index':str(temp_header)+'_'+str(temp_written_string)
                                },
                                children=[
                                    dropdown_options[temp_header][temp_written_string][0]['label']
                                ]
                            ),
                        ),
                        #the dropdown for strings that are close
                        dbc.Col(
                            dcc.Dropdown(
                                id={
                                    'type':'dropdown_similar_strings',
                                    'index':str(temp_header)+'_'+str(temp_written_string)
                                },
                                options=[label_value_pair for label_value_pair in dropdown_options[temp_header][temp_written_string]],
                                optionHeight=60
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
                                options=['Type substring to populate options.'],
                                optionHeight=60
                            ),  
                        ),
                        #the empty input to create your own
                        dbc.Col(
                            dcc.Input(
                                id={
                                    'type':'input_curation',
                                    'index':str(temp_header)+'_'+str(temp_written_string)
                                },
                                placeholder="Nothing matches - Enter New"
                            )
                        )

                    ]
                )
            )

    return [output_children]


@callback(
    [
        Output(component_id={'type':'dropdown_empty_options','index':MATCH},component_property='options'),
    ],
    [
        Input(component_id={'type':'dropdown_empty_options','index':MATCH},component_property='search_value'),
    ],
    [
        State(component_id={'type':'header_written_pair','index':MATCH},component_property="children"),
    ],
)
def update_options(
    dropdown_empty_options_search_value,
    header_written_pair_children
):
    '''
    generates the labels in the substring dropdown
    ISSUE 36
    ISSUE 37
    '''


    if not dropdown_empty_options_search_value:
        raise PreventUpdate

    # print(dropdown_empty_options_search_value)
    # print(header_written_pair_children)

    this_header_type=header_written_pair_children[0].split(':')[0].split('.')[0]
    if this_header_type not in HEADERS_WITH_SHORT_NGRAMS:
        if len(dropdown_empty_options_search_value)<3:
            raise PreventUpdate

    current_index=ctx.triggered_id['index'].split('_')[0].split('.')[0]
    #need to access the index
    # print(ctx.triggered_id)
    # print(current_index)
    # print('y halo thar')

    # temp_valid_values=conglomerate_vocabulary_panda_dict[current_index].loc[
    #     conglomerate_vocabulary_panda_dict[current_index]['valid_string'].str.startswith(dropdown_empty_options_search_value)
    # ].drop_duplicates(subset=('main_string')).sort_values(['use_count','valid_string'],ascending=[False,True])['valid_string'].tolist()

    # temp_main_values=conglomerate_vocabulary_panda_dict[current_index].loc[
    #     conglomerate_vocabulary_panda_dict[current_index]['valid_string'].str.startswith(dropdown_empty_options_search_value)
    # ].drop_duplicates(subset=('main_string')).sort_values(['use_count','valid_string'],ascending=[False,True])['main_string'].tolist()

    temp_values=conglomerate_vocabulary_panda_dict[current_index].loc[
        conglomerate_vocabulary_panda_dict[current_index]['valid_string'].str.startswith(dropdown_empty_options_search_value)
    ].drop_duplicates(subset=('main_string')).sort_values(['use_count','valid_string'],ascending=[False,True])[['valid_string','main_string']].agg(' AKA '.join, axis=1).tolist()

    # print(temp_values)
    return [[
        {   #this form does not match the others. the others take the valid string and plug it into the json. "this is an oldier comment? plb after json to pandas"
            'label': temp_string,
            'value': temp_string
        } for temp_string in temp_values
    ]]



def update_excel_sheet_curated_sample_formatting(workbook,worksheet,store_panda):
    '''
    i think that we should rewrite "current_none_null_cell_phrase" to be "previous"
    whereas current non null cell can stay
    '''



    #take care of teh top row, merged cells
    last_index=store_panda.index[-1]
    current_cell=0
    color_list_counter=0
    columns_to_merge=0
    for temp_col in store_panda.columns:
        
        if pd.isna(store_panda.at[last_index,temp_col])==True:
            columns_to_merge+=1
        elif pd.isna(store_panda.at[last_index,temp_col])==False and current_cell!=0:
            temp_format=workbook.add_format(
                {
                    'align': 'center',
                    'valign': 'vcenter',
                    'fg_color': COLOR_LIST[color_list_counter]
                }
            )            
            color_list_counter+=1
            start_cell_xl=xl_rowcol_to_cell(0,current_non_null_cell)

            if columns_to_merge==0:
                current_non_null_cell=current_cell
                worksheet.write(start_cell_xl,current_non_null_cell_phrase,temp_format)
                current_non_null_cell_phrase=store_panda.at[last_index,temp_col]

            elif columns_to_merge>0:
                
                end_cell_xl=xl_rowcol_to_cell(0,current_non_null_cell+columns_to_merge)
                current_non_null_cell=current_cell
                
                worksheet.merge_range(
                    start_cell_xl+':'+end_cell_xl,
                    current_non_null_cell_phrase,
                    temp_format
                )   
            current_non_null_cell_phrase=store_panda.at[last_index,temp_col]
            columns_to_merge=0

        elif pd.isna(store_panda.at[last_index,temp_col])==False and current_cell==0:
            current_non_null_cell=0
            current_non_null_cell_phrase=store_panda.at[last_index,temp_col]

        current_cell+=1
    #once we reach the end, perform the merge operation
    temp_format=workbook.add_format(
        {
            'align': 'center',
            'valign': 'vcenter',
            'fg_color': COLOR_LIST[color_list_counter]
        }
    )            
    color_list_counter+=1
    start_cell_xl=xl_rowcol_to_cell(0,current_non_null_cell)
    if columns_to_merge==0:
        worksheet.write(start_cell_xl,current_non_null_cell_phrase,temp_format)
    elif columns_to_merge>0:
        
        end_cell_xl=xl_rowcol_to_cell(0,current_non_null_cell+columns_to_merge)
        current_non_null_cell=current_cell
        #current_non_null_cell_phrase=store_panda.at[last_index,temp_col]
        worksheet.merge_range(
            start_cell_xl+':'+end_cell_xl,
            current_non_null_cell_phrase,
            temp_format
        )   



    return workbook,worksheet

@callback(
    [
        Output(component_id="Div_new_vocab_error_messages", component_property="children"),
        Output(component_id="download_curated_form", component_property="data")
    ],
    [
        Input(component_id='button_download_curated', component_property="n_clicks")
    ],
    [
        State(component_id="main_store",component_property="data"),
        State(component_id={'type':'header_written_pair','index':ALL},component_property="children"),
        State(component_id={'type':'H6_best_guess','index':ALL},component_property="children"),
        State(component_id={'type':'dropdown_similar_strings','index':ALL},component_property="value"),
        State(component_id={'type':'dropdown_empty_options','index':ALL},component_property="value"),
        State(component_id={'type':'input_curation','index':ALL},component_property="value"),
        State(component_id={'type':'dropdown_similar_strings','index':ALL},component_property="options"),
    ],
    prevent_initial_call=True
)
def download_curated_forum(
    button_download_curated_n_clicks,
    main_store_data,
    header_written_pair_children_ALL,
    #note that these guys are used, but are named with eval so not colored here
    H6_best_guess_children_ALL,
    dropdown_similar_strings_value_ALL,
    dropdown_empty_options_value_ALL,
    input_curation_value_ALL,
    dropdown_similar_strings_options_ALL
):
    '''
    downloading the curated data does several things
    now:
        gives the user a curated excel sheet
        update the vocabulary
        update the use_count

    future:
        provide an endpoint

    '''

    store_panda=pd.read_json(main_store_data['input_dataframe'],orient='records')

    # print('')
    # print(dropdown_similar_strings_options_ALL)
    #[None, None, 'oooga', 'booga', 'muhkidney', None, None, None, None, None, None, None]
    #print(input_curation_value_ALL)
    #print('store_panda')
    #print(store_panda)

    #if someone dtypes something into the new suggestions, then removes them, the value becomes '' not None
    #need to set '' to none
    for i in range(len(input_curation_value_ALL)):
        if input_curation_value_ALL[i]=='':
            input_curation_value_ALL[i]=None

    #print('')
    # print(main_store_data['group_to_header_dict_curated'])
    # print('')
    # print(main_store_data['group_to_text_dict_curated'])

    my_NewVocabularyUploadChecker=newvocabularyuploadchecker.NewVocabularyUploadChecker(input_curation_value_ALL)
    my_NewVocabularyUploadChecker.check_char_length()
    my_NewVocabularyUploadChecker.verify_string_absence()
    #print(my_NewVocabularyUploadChecker.error_list)
    #print('error list')
    if len(my_NewVocabularyUploadChecker.error_list)>0:
        output_div_children=dbc.Row(
            children=[
                dbc.Col(width=4),
                dbc.Col(
                    children=[html.H6(element,style={'color':'red','text-align':'center'}) for element in my_NewVocabularyUploadChecker.error_list],
                    width=4,
                    #align='center'
                ),
                dbc.Col(width=4)
            ]
        )   
        download_data=None
        return [output_div_children,download_data]
    #this is used in the use_count update
    #the logic is 
    #during the next for loop we create 
    #[(header,replacement)] which will become
    #main_string
    #because the headers are synonyms with vocabulary pandas we can then just
    #increment main string's corresponding 'use_count' column
    header_replacement_list=list()

    #this loop updates the stored dictr that becomes the user output excel file
    #temp_header_written_pair is the thing on the far left, eg "species: arabidopsis"
    for i,temp_header_written_pair in enumerate(header_written_pair_children_ALL):
    #for i,temp_header_written_pair in enumerate(dropdown_empty_options_value_ALL):
        #children are stored as list, so access with 0
        temp_header=temp_header_written_pair[0].split(': ')[0]
        #temp_header_core_vocabulary=temp_header.split('.')[0]

        temp_written_string=temp_header_written_pair[0].split(': ')[1]

        #chose the element that we want to substitute using the priority list
        #kidn of a sloppy way to do this
        #we do j in order to skp the first element, which is guaranteed to not be None
        #curation column is a list naturally
        for j,curation_column in enumerate(priority_list):
            if j==0:
                #we actually fetch the top dropdown option, not the H6 value
                #because we want it to include the "AKA"
                #the old approach is this, below. the [0] is because children are lists
                #temp_replacement=eval(curation_column)[i][0]
                temp_replacement=dropdown_similar_strings_options_ALL[i][0]['value']
                continue
            if eval(curation_column)[i] is not None:
                temp_replacement=eval(curation_column)[i]

            
        #ISSUE 37
        #it will becomes the case that nothing does *not* have aka as its value
        #i dont think that we want to keep just the valid string that we map to, however
        #this can lead to ambiguities, for example "purple sulfur bacteria" or "tsetse fly"
        #are valid strings for multiple main_strings
        #if ' AKA ' in temp_replacement:
        #    temp_replacement=temp_replacement.split(' AKA ')[0]

        # print(f'{temp_header} {temp_written_string}: {temp_replacement}')

        #ISSUE 24
        #we skip the very early forms of empty lists
        if temp_replacement!='no options available':
            header_replacement_list.append((temp_header,temp_replacement))

        
        #basically, we had a problem where the panda headers were something like species.1.0
        #and the tempheaders were just 'species' which is ambiguous
        #so we just opted to do the lazy, not perfect thing and try to replace all. slightly dangerous
        for temp_column in store_panda.columns:
            if temp_header in temp_column:
                store_panda[temp_column].replace(
                    #to_replace=temp_written_string,
                    #value=temp_replacement,
                    {temp_written_string:temp_replacement},
                    inplace=True
                )

    #remove things left of ' AKA '
    for temp_column in store_panda.columns:
        # print(store_panda[temp_column].astype(str).str.contains(' AKA '))
        store_panda[temp_column].mask(
            cond=store_panda[temp_column].astype(str).str.contains(' AKA '),
            other=store_panda[temp_column].astype(str).str.split(' AKA ').str[1],
            inplace=True
        )

    empty_columns=[temp_col for temp_col in store_panda if len([element for element in store_panda[temp_col][:-1].unique() if pd.isnull(element)==False])==0]
    store_panda.drop(empty_columns,axis='columns',inplace=True)
    #print(store_panda)
        # #remove the left hand side of AKA
        # for temp_column in store_panda.columns:
        #     if temp_header in temp_column:
        #temp_remove_aka_dict=dict()
        # #         #print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
        # #         #print(store_panda[temp_column].unique())
        #for temp_string_with_aka in store_panda[temp_column].unique():
        # #             #print(temp_string_with_aka)
         #   if (((' AKA ') in temp_string_with_aka) and (temp_string_with_aka is not None) and (pd.isnull(temp_string_with_aka)==False)):
        # #                 #print(temp_string_with_aka.split(' AKA ')[1])
         #       temp_remove_aka_dict[temp_string_with_aka]=temp_string_with_aka.split(' AKA ')
         #   if len(temp_remove_aka_dict.keys())>0:        
         #       store_panda[temp_column].replace(
        #             #to_replace=temp_written_string,
        #             #value=temp_replacement,
        #             #{temp_string_with_aka:temp_string_with_aka.split(' AKA ')[1] for temp_string_with_aka in store_panda[temp_column].tolist() if (((' AKA ') in temp_string_with_aka) and (temp_string_with_aka is not None))},
         #           temp_remove_aka_dict,
         #           inplace=True
          #      )
        
        # try:
        #     temp_replacement=temp_replacement.split(' AKA ')[1]
        # except:
        #     pass

        #########NOTE##########3
        #need to have some sort of special case for "no options available" for things that start empty    

    # print('===========================')
    # print('===========================')
    # print(store_panda)

    #print(store_panda)
    #print('the output??')


    output_stream=io.BytesIO()
    temp_writer=pd.ExcelWriter(output_stream,engine='xlsxwriter')

    empty_df=pd.DataFrame()
    empty_df.to_excel(temp_writer,sheet_name='title_page',index=False)
    #skip the last row which has the merger archetype info
    store_panda.iloc[:-1,:].to_excel(
        temp_writer,
        sheet_name='sample_sheet_curated',
        index=False,
        startrow=1,
        #take off the weird .0.1 etc
        header=[element.split('.')[0] for element in store_panda.columns]
    )
    #empty_df.to_excel(temp_writer,sheet_name='sample_sheet_curated',index=False)


    #https://xlsxwriter.readthedocs.io/working_with_pandas.html
    #https://community.plotly.com/t/generate-multiple-tabs-in-excel-file-with-dcc-send-data-frame/53460/7
    workbook=temp_writer.book
    worksheet=temp_writer.sheets['sample_sheet_curated']
    workbook,worksheet=update_excel_sheet_curated_sample_formatting(workbook,worksheet,store_panda)

    worksheet.autofit()

    worksheet=temp_writer.sheets['title_page']
    worksheet.hide_gridlines()
    worksheet.write('B2','Enjoy the curations :)')
    #worksheet.write('B3','Please leave unused metadata blank.')

    
    
    

    temp_writer.save()
    temp_data=output_stream.getvalue()
    #output_excel

    #ISSUE 38
    #we want to expand the vocabulary on the fly. 
    #this  forloop and the one below apply only to the "reject suggestions, create new" column
    #for each non null reject suggetsion
    #first, we want to compile a total list of new vocabulary so that we dont train 3x if there are 3 new species
    new_vocab_dict=dict()
    for i,new_vocabulary_word in enumerate(input_curation_value_ALL):
        if new_vocabulary_word is not None:
            try:
                new_vocab_dict[
                    #notice that here we use the temp_header core vocabulary pattern: .split('.')[0]
                    header_written_pair_children_ALL[i][0].split(': ')[0].split('.')[0]
                ].append(new_vocabulary_word)
            except KeyError:
                new_vocab_dict[
                    header_written_pair_children_ALL[i][0].split(': ')[0].split('.')[0]
                ]=[new_vocabulary_word]
    #print('new vocabulary dict')
    #print(new_vocab_dict)
    #print('')
    #now, for each key in this dict, append to the corresponding panda in the conglomerate dict, then output it again
    for temp_key in new_vocab_dict.keys():
        appending_dict={
            'valid_string':[],
            'node_id':[],
            'main_string':[],
            'ontology':[],
            'use_count':[]
        }
        for temp_addition in new_vocab_dict[temp_key]:
            appending_dict['valid_string'].append(temp_addition)
            appending_dict['node_id'].append(temp_addition)
            appending_dict['main_string'].append(temp_addition)
            appending_dict['ontology'].append('userAdded')
            appending_dict['use_count'].append(1)
        appending_panda=pd.DataFrame.from_dict(appending_dict)

        conglomerate_vocabulary_panda_dict[temp_key]=pd.concat(
            [conglomerate_vocabulary_panda_dict[temp_key],appending_panda],
            axis='index',
            ignore_index=True,
        )
        #the pattern for new suggestions is that the given string becomes the valid_string, main_string, and node_id (something like that)
        #to make sure that a user doesnt put someonething that already exists
        conglomerate_vocabulary_panda_dict[temp_key].drop_duplicates(subset=('valid_string','main_string'),ignore_index=True,inplace=True)
        #print(conglomerate_vocabulary_panda_dict[temp_key])
    #print(con)

    #print('===========================')
    #print(conglomerate_vocabulary_panda_dict)
    #print(conglomerate_vocabulary_panda_dict['species'].loc[conglomerate_vocabulary_panda_dict['species'].main_string.str.contains('musculus')])
    #this loop apply for every row in the curation table
    #the purpose of this loop is to increment the use_count
    #print(header_replacement_list)
    for temp_tuple in header_replacement_list:
        temp_header_core_vocabulary=temp_tuple[0].split('.')[0]
        #for each thing to replace 
        #get the corresponding panda
        #from that, get the corresponding main string
        #if there is more thjan one unique main string, raise an exception
        #otherwise, 
        temp_valid_string=temp_tuple[1].split(' AKA ')[0]
        #AKA wont be in there if new vocabulary is added
        if ' AKA ' in temp_tuple[1]:
            temp_main_string=temp_tuple[1].split(' AKA ')[1]
        else:
            temp_main_string=temp_tuple[1].split(' AKA ')[0]
        corresponding_main_string_list=conglomerate_vocabulary_panda_dict[temp_header_core_vocabulary].loc[
            (conglomerate_vocabulary_panda_dict[temp_header_core_vocabulary]['valid_string']==temp_valid_string) &
            (conglomerate_vocabulary_panda_dict[temp_header_core_vocabulary]['main_string']==temp_main_string)
        ]['main_string'].unique()
        #print(conglomerate_vocabulary_panda_dict)
        #print(temp_tuple)
        #print(temp_valid_string)
        #print(temp_main_string)
        #print(corresponding_main_string_list)
        if len(corresponding_main_string_list)>1:
            # print(corresponding_main_string_list)
            raise Exception('there should only be one main string for a valid string, found multiple')
        corresponding_main_string=corresponding_main_string_list[0]
        #where value is true, keep original
        conglomerate_vocabulary_panda_dict[temp_header_core_vocabulary]['use_count']=conglomerate_vocabulary_panda_dict[temp_header_core_vocabulary]['use_count'].where(
            conglomerate_vocabulary_panda_dict[temp_header_core_vocabulary]['main_string']!=corresponding_main_string,
            #other=conglomerate_vocabulary_panda_dict[temp_header_core_vocabulary]['use_count']+1
            other=1
        )

    #this set of instructions occurs for every vocabulary that is referenced by at least one row
    taxonomies_referenced={element[0].split('.')[0] for element in header_replacement_list}
    for temp_key in taxonomies_referenced:
        conglomerate_vocabulary_panda_dict[temp_key].to_pickle(f'additional_files/conglomerate_vocabulary_panda_{temp_key}.bin')

    #this set of instructions occurs for vocabularies which are incremented at least once.
    #this set of instructions should probably go up above 
    #now we create a new vectorizer and nearest neighbors model
    for temp_key in new_vocab_dict.keys():
        temp_model_vocabulary=conglomerate_vocabulary_panda_dict[temp_key]['valid_string'].unique()
        temp_TfidfVectorizer=TfidfVectorizer(
            analyzer='char',
            ngram_range=ngram_limits_per_heading_json[temp_key],
            use_idf=False,
            norm=None
            #max_df=1,
            #max_df=1,
            #min_df=0.001
        )
        temp_tfidf_matrix=temp_TfidfVectorizer.fit_transform(temp_model_vocabulary)
        with open(f'additional_files/tfidfVectorizer_{temp_key}.bin','wb') as fp:
            pickle.dump(temp_TfidfVectorizer,fp)
        
        temp_NN_model=NearestNeighbors(
            n_neighbors=50,
            n_jobs=5,
            metric='cosine'
        )
        temp_NN_model.fit(temp_tfidf_matrix)
        with open(f'additional_files/NearestNeighbors_{temp_key}.bin','wb') as fp:
            pickle.dump(temp_NN_model,fp)        
    #update the unique strings list
    for temp_key in new_vocab_dict.keys():
        vocabulary_dict[temp_key]=pd.DataFrame.from_dict(
            conglomerate_vocabulary_panda_dict[temp_key]['valid_string'].unique()
        )
        vocabulary_dict[temp_key].to_pickle(f'additional_files/unique_valid_strings_{temp_key}.bin')

    return [
        None,dcc.send_bytes(temp_data,"binbase_sample_ingestion_form_curated.xlsx")
    ]
