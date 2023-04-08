# import dash
# from dash import dcc, html,dash_table,callback, ctx,MATCH,ALL
# import plotly.express as px
# import dash_bootstrap_components as dbc
# from dash.dependencies import Input, Output, State
# import numpy as np
# from dash.exceptions import PreventUpdate

# from sklearn.feature_extraction.text import TfidfVectorizer
# from sklearn.neighbors import NearestNeighbors
# from sklearn.exceptions import NotFittedError
# import json
# import pandas as pd
# import io
# from xlsxwriter.utility import xl_rowcol_to_cell
# import requests

# dash.register_page(__name__, path='/curate-and-download')

# base_url_api = "http://127.0.0.1:4999/"

# #get the headers and their subset definitions
# with open('additional_files/subset_per_heading.json', 'r') as fp:
#     subset_per_heading_json=json.load(fp)

# PRIORITY_LIST=[
#     'H6_best_guess_children_ALL',
#     'dropdown_similar_strings_value_ALL',
#     'dropdown_empty_options_value_ALL',
#     'input_curation_value_ALL'
# ]

# HEADERS_WITH_SHORT_NGRAMS={'heightUnit','weightUnit','ageUnit','massUnit','volumeUnit','timeUnit','drugDoseUnit'}
# COLOR_LIST=['red','orange','yellow','green','lime','sky','khaki','red','orange','yellow','green','lime','sky','khaki','red','orange','yellow','green','lime','sky','khaki']
# NEIGHBORS_TO_RETRIEVE=100



# def parse_stored_excel_file(store_panda):
#     '''
#     extracts the {header:[written_string]} relationship
#     '''
#     output_dict=dict()
#     for temp_header in store_panda.columns:
#         output_dict[temp_header]=store_panda[temp_header].dropna().unique().tolist()
#     return output_dict

# def generate_dropdown_options_api(written_strings_per_category):
    
#     output_dict=dict()
#     for temp_header in written_strings_per_category.keys():
#         #temp_core_vocabulary allows for the processing of multiple of the same header type, like species, species.1, species.2 etc
#         #if for example someone had a chimera.
#         temp_header_core_vocabulary=temp_header.split('.')[0]

#         #we dont curate certain categories esp numerical like height, weight, etc
#         #we recombine those at the end of the curate function
#         if temp_header_core_vocabulary not in subset_per_heading_json.keys():
#             continue
        
#         output_dict[temp_header]=dict()
#         for temp_written_string in written_strings_per_category[temp_header]:
#             output_dict[temp_header][temp_written_string]=list()

#             #if the tfidft vectorizer isnt fitted
#             #the neighbors isnt fitted either
#             #this happens when the vocabulary ingester is just getting started
#             predict_request={
#                 "header":temp_header_core_vocabulary,
#                 "written_strings":[temp_written_string],
#                 "neighbors_to_retrieve":NEIGHBORS_TO_RETRIEVE
#             }
            
#             response = requests.post(base_url_api + "/predictvocabularytermsresource/", json=predict_request)
#             this_strings_neighbors = pd.read_json(response.json(), orient="records")    

#             if (len(this_strings_neighbors.index)==0) or (this_strings_neighbors.applymap(pd.isnull).all().all() == True):
#                 output_dict[temp_header][temp_written_string].append(
#                         {
#                             'label':'no options available',
#                             'value':'no options available'
#                         }
#                     )
#                 continue
                
#             for index,series in this_strings_neighbors.iterrows():
#                 #in each of the options, having "thing AKA thing" is 
#                 if series['valid_string']==series['main_string'].lower():            
#                     output_dict[temp_header][temp_written_string].append(
#                         {
#                             'label':series['valid_string'],#+' NODE '+series['node_id'],
#                             'value':series['valid_string']+' AKA '+series['main_string']                
#                         }
#                     )
#                 else:
#                     output_dict[temp_header][temp_written_string].append(
#                         {
#                             'label':series['valid_string']+' AKA '+series['main_string'],#+' NODE '+series['node_id'],
#                             'value':series['valid_string']+' AKA '+series['main_string']#+' NODE '+series['node_id']                
#                         }
#                     )

#     return output_dict

# layout = html.Div(
#     children=[
#         dcc.Download(id="download_curated_form"),
#         html.Br(),
#         html.Br(),
#         dbc.Row(
#             children=[
#                 html.Div(
#                     id='here_is_where_we_put_the curation_interface'
#                 )
#             ]
#         ),
#         html.Br(),
#         html.Br(),
#         dbc.Row(
#             children=[
#                 html.Div(
#                     dbc.Button(
#                         'Download Curated Form',
#                         id='button_download_curated',
#                     ),
#                     className="d-grid gap-2 col-6 mx-auto",
#                 ),
#             ]
#         ),
#         html.Br(),
#         html.Br(),
#         html.Div(id='Div_new_vocab_error_messages'),
#     ],
# )


# @callback(
#     [
#         Output(component_id="here_is_where_we_put_the curation_interface", component_property="children"),
#         #Output(component_id="table_curation", component_property="data"),
#         #Output(component_id="table_curation", component_property="dropdown_data"),
#         #Output(component_id="main_store",component_property="data")
#     ],
#     [
#         #Input(component_id="upload_form", component_property="contents"),
#         #Input(component_id="load_interval", component_property="n_intervals")
#         Input(component_id="url", component_property="href")
#     ],
#     [
#         #State(component_id="upload_form", component_property="filename"),
#         State(component_id="main_store",component_property="data"),
#     ],
#     #prevent_initial_call=True
# )
# def curate_data(
#     url_href,
#     main_store_data
# ):
#     '''
#     '''
#     url_href_page_location=url_href.split('/')[-1]
#     if url_href_page_location!='curate-and-download':
#         raise PreventUpdate

#     store_panda=pd.read_json(main_store_data['input_dataframe'],orient='records')
#     store_panda=store_panda.iloc[:-1,:]

#     written_strings_per_category=parse_stored_excel_file(store_panda)

#     dropdown_options=generate_dropdown_options_api(written_strings_per_category)

#     output_children=list()

#     output_children.append(
#         dbc.Row(
#             children=[
#                 dbc.Col(
#                     children=[
#                         html.H3('User Entry'),
#                         html.Br()                        
#                     ]
#                 ),    
#                 dbc.Col(
#                     html.H3('Best Guess')
#                 ),
#                 dbc.Col(
#                     html.H3('Similar Guesses')
#                 ),
#                 dbc.Col(
#                     html.H3('Type to match text')  
#                 ),
#                 dbc.Col(
#                     html.H3('Reject suggestions, create new')
#                 )

#             ]
#         )
#     )
    
#     #there is a row per (temp_header,temp_written_string)
#     for temp_header in dropdown_options.keys():
#         for temp_written_string in dropdown_options[temp_header].keys():
#             output_children.append(
#                 dbc.Row(
#                     children=[
#                         #dbc.Col(width=1),
#                         dbc.Col(
#                             html.H6(
#                                 id={
#                                     'type':'header_written_pair',
#                                     'index':str(temp_header)+'_'+str(temp_written_string)
#                                 },
#                                 children=[
#                                     str(temp_header).split('.')[0]+': '+str(temp_written_string)
#                                     #str(temp_header)+': '+str(temp_written_string)
#                                 ]
#                             )
#                         ),    
#                         dbc.Col(
#                             html.H6(
#                                 id={
#                                     'type':'H6_best_guess',
#                                     'index':str(temp_header)+'_'+str(temp_written_string)
#                                 },
#                                 children=[
#                                     dropdown_options[temp_header][temp_written_string][0]['label']
#                                 ]
#                             ),
#                         ),
#                         #the dropdown for strings that are close
#                         dbc.Col(
#                             dcc.Dropdown(
#                                 id={
#                                     'type':'dropdown_similar_strings',
#                                     'index':str(temp_header)+'_'+str(temp_written_string)
#                                 },
#                                 options=[label_value_pair for label_value_pair in dropdown_options[temp_header][temp_written_string]],
#                                 optionHeight=60
#                             )
#                         ),
#                         #the dropdown with completely empty boxes
#                         dbc.Col(
#                             dcc.Dropdown(
#                                 id={
#                                     'type':'dropdown_empty_options',
#                                     'index':str(temp_header)+'_'+str(temp_written_string)
#                                 },
#                                 multi=False,
#                                 placeholder='Type compound name to search',
#                                 options=['Type substring to populate options.'],
#                                 optionHeight=60
#                             ),  
#                         ),
#                         #the empty input to create your own
#                         dbc.Col(
#                             dcc.Input(
#                                 id={
#                                     'type':'input_curation',
#                                     'index':str(temp_header)+'_'+str(temp_written_string)
#                                 },
#                                 placeholder="Nothing matches - Enter New"
#                             )
#                         )

#                     ]
#                 )
#             )

#     return [output_children]


# @callback(
#     [
#         Output(component_id={'type':'dropdown_empty_options','index':MATCH},component_property='options'),
#     ],
#     [
#         Input(component_id={'type':'dropdown_empty_options','index':MATCH},component_property='search_value'),
#     ],
#     [
#         State(component_id={'type':'header_written_pair','index':MATCH},component_property="children"),
#     ],
# )
# def update_options(
#     dropdown_empty_options_search_value,
#     header_written_pair_children
# ):
#     '''
#     generates the labels in the substring dropdown
#     ISSUE 36
#     ISSUE 37
#     '''


#     if not dropdown_empty_options_search_value:
#         raise PreventUpdate

#     this_header_type=header_written_pair_children[0].split(':')[0].split('.')[0]
#     if this_header_type not in HEADERS_WITH_SHORT_NGRAMS:
#         if len(dropdown_empty_options_search_value)<3:
#             raise PreventUpdate

#     current_index=ctx.triggered_id['index'].split('_')[0].split('.')[0]

#     outbound_json={
#         'header':current_index,
#         'substring':dropdown_empty_options_search_value
#     }

#     temp_values=requests.post(base_url_api+'/generatesubstringmatches/',json=outbound_json).json()


#     print(temp_values)
#     return [[
#         { 
#             'label': temp_string,
#             'value': temp_string
#         } for temp_string in temp_values
#     ]]



# def update_excel_sheet_curated_sample_formatting(workbook,worksheet,store_panda):
#     '''
#     i think that we should rewrite "current_none_null_cell_phrase" to be "previous"
#     whereas current non null cell can stay
#     '''

#     #take care of teh top row, merged cells
#     last_index=store_panda.index[-1]
#     current_cell=0
#     color_list_counter=0
#     columns_to_merge=0
#     for temp_col in store_panda.columns:
        
#         if pd.isna(store_panda.at[last_index,temp_col])==True:
#             columns_to_merge+=1
#         elif pd.isna(store_panda.at[last_index,temp_col])==False and current_cell!=0:
#             temp_format=workbook.add_format(
#                 {
#                     'align': 'center',
#                     'valign': 'vcenter',
#                     'fg_color': COLOR_LIST[color_list_counter]
#                 }
#             )            
#             color_list_counter+=1
#             start_cell_xl=xl_rowcol_to_cell(0,current_non_null_cell)

#             if columns_to_merge==0:
#                 current_non_null_cell=current_cell
#                 worksheet.write(start_cell_xl,current_non_null_cell_phrase,temp_format)
#                 current_non_null_cell_phrase=store_panda.at[last_index,temp_col]

#             elif columns_to_merge>0:
                
#                 end_cell_xl=xl_rowcol_to_cell(0,current_non_null_cell+columns_to_merge)
#                 current_non_null_cell=current_cell
                
#                 worksheet.merge_range(
#                     start_cell_xl+':'+end_cell_xl,
#                     current_non_null_cell_phrase,
#                     temp_format
#                 )   
#             current_non_null_cell_phrase=store_panda.at[last_index,temp_col]
#             columns_to_merge=0

#         elif pd.isna(store_panda.at[last_index,temp_col])==False and current_cell==0:
#             current_non_null_cell=0
#             current_non_null_cell_phrase=store_panda.at[last_index,temp_col]

#         current_cell+=1
#     #once we reach the end, perform the merge operation
#     temp_format=workbook.add_format(
#         {
#             'align': 'center',
#             'valign': 'vcenter',
#             'fg_color': COLOR_LIST[color_list_counter]
#         }
#     )            
#     color_list_counter+=1
#     start_cell_xl=xl_rowcol_to_cell(0,current_non_null_cell)
#     if columns_to_merge==0:
#         worksheet.write(start_cell_xl,current_non_null_cell_phrase,temp_format)
#     elif columns_to_merge>0:
        
#         end_cell_xl=xl_rowcol_to_cell(0,current_non_null_cell+columns_to_merge)
#         current_non_null_cell=current_cell
#         #current_non_null_cell_phrase=store_panda.at[last_index,temp_col]
#         worksheet.merge_range(
#             start_cell_xl+':'+end_cell_xl,
#             current_non_null_cell_phrase,
#             temp_format
#         )   

#     return workbook,worksheet

# @callback(
#     [
#         Output(component_id="Div_new_vocab_error_messages", component_property="children"),
#         Output(component_id="download_curated_form", component_property="data")
#     ],
#     [
#         Input(component_id='button_download_curated', component_property="n_clicks")
#     ],
#     [
#         State(component_id="main_store",component_property="data"),
#         State(component_id={'type':'header_written_pair','index':ALL},component_property="children"),
#         State(component_id={'type':'H6_best_guess','index':ALL},component_property="children"),
#         State(component_id={'type':'dropdown_similar_strings','index':ALL},component_property="value"),
#         State(component_id={'type':'dropdown_empty_options','index':ALL},component_property="value"),
#         State(component_id={'type':'input_curation','index':ALL},component_property="value"),
#         State(component_id={'type':'dropdown_similar_strings','index':ALL},component_property="options"),
#     ],
#     prevent_initial_call=True
# )
# def download_curated_forum(
#     button_download_curated_n_clicks,
#     main_store_data,
#     header_written_pair_children_ALL,
#     #note that these guys are used, but are named with eval so not colored here
#     H6_best_guess_children_ALL,
#     dropdown_similar_strings_value_ALL,
#     dropdown_empty_options_value_ALL,
#     input_curation_value_ALL,
#     dropdown_similar_strings_options_ALL
# ):
#     '''
#     downloading the curated data does several things
#     now:
#         gives the user a curated excel sheet
#         update the vocabulary
#         update the use_count

#     future:
#         provide an endpoint

#     '''

#     store_panda=pd.read_json(main_store_data['input_dataframe'],orient='records')

#     #if someone dtypes something into the new suggestions, then removes them, the value becomes '' not None
#     #need to set '' to none
#     for i in range(len(input_curation_value_ALL)):
#         if input_curation_value_ALL[i]=='':
#             input_curation_value_ALL[i]=None

#     new_vocabulary_error_list=requests.post(base_url_api+'/validatetermsfortraining/',json={'new_vocabulary':input_curation_value_ALL}).json()['errors']

#     if len(new_vocabulary_error_list)>0:
#         output_div_children=dbc.Row(
#             children=[
#                 dbc.Col(width=4),
#                 dbc.Col(
#                     children=[html.H6(element,style={'color':'red','text-align':'center'}) for element in new_vocabulary_error_list],
#                     width=4,
#                 ),
#                 dbc.Col(width=4)
#             ]
#         )   
#         download_data=None
#         return [output_div_children,download_data]
#     #this is used in the use_count update
#     #the logic is 
#     #during the next for loop we create 
#     #[(header,replacement)] which will become
#     #main_string
#     #because the headers are synonyms with vocabulary pandas we can then just
#     #increment main string's corresponding 'use_count' column
#     header_replacement_list=list()

#     #this loop updates the stored dictr that becomes the user output excel file
#     #temp_header_written_pair is the thing on the far left, eg "species: arabidopsis"
#     for i,temp_header_written_pair in enumerate(header_written_pair_children_ALL):
#         #children are stored as list, so access with 0
#         temp_header=temp_header_written_pair[0].split(': ')[0]

#         temp_written_string=temp_header_written_pair[0].split(': ')[1]

#         #chose the element that we want to substitute using the priority list
#         #kidn of a sloppy way to do this
#         #we do j in order to skp the first element, which is guaranteed to not be None
#         #curation column is a list naturally
#         for j,curation_column in enumerate(PRIORITY_LIST):
#             if j==0:
#                 #we actually fetch the top dropdown option, not the H6 value
#                 #because we want it to include the "AKA"
#                 #the old approach is this, below. the [0] is because children are lists
#                 #temp_replacement=eval(curation_column)[i][0]
#                 temp_replacement=dropdown_similar_strings_options_ALL[i][0]['value']
#                 continue
#             if eval(curation_column)[i] is not None:
#                 temp_replacement=eval(curation_column)[i]
            
#         #ISSUE 37
#         #it will becomes the case that nothing does *not* have aka as its value
#         #i dont think that we want to keep just the valid string that we map to, however
#         #this can lead to ambiguities, for example "purple sulfur bacteria" or "tsetse fly"
#         #are valid strings for multiple main_strings

#         #ISSUE 24
#         #we skip the very early forms of empty lists
#         if temp_replacement!='no options available':
#             header_replacement_list.append((temp_header,temp_replacement))
        
#         #basically, we had a problem where the panda headers were something like species.1.0
#         #and the tempheaders were just 'species' which is ambiguous
#         #so we just opted to do the lazy, not perfect thing and try to replace all. slightly dangerous
#         for temp_column in store_panda.columns:
#             if temp_header in temp_column:
#                 store_panda[temp_column].replace(
#                     {temp_written_string:temp_replacement},
#                     inplace=True
#                 )

#     #remove things left of ' AKA '
#     for temp_column in store_panda.columns:
#         store_panda[temp_column].mask(
#             cond=store_panda[temp_column].astype(str).str.contains(' AKA '),
#             other=store_panda[temp_column].astype(str).str.split(' AKA ').str[1],
#             inplace=True
#         )

#     empty_columns=[temp_col for temp_col in store_panda if len([element for element in store_panda[temp_col][:-1].unique() if pd.isnull(element)==False])==0]
#     store_panda.drop(empty_columns,axis='columns',inplace=True)

#     output_stream=io.BytesIO()
#     temp_writer=pd.ExcelWriter(output_stream,engine='xlsxwriter')

#     empty_df=pd.DataFrame()
#     empty_df.to_excel(temp_writer,sheet_name='title_page',index=False)
#     #skip the last row which has the merger archetype info
#     store_panda.iloc[:-1,:].to_excel(
#         temp_writer,
#         sheet_name='sample_sheet_curated',
#         index=False,
#         startrow=1,
#         #take off the weird .0.1 etc
#         header=[element.split('.')[0] for element in store_panda.columns]
#     )

#     #https://xlsxwriter.readthedocs.io/working_with_pandas.html
#     #https://community.plotly.com/t/generate-multiple-tabs-in-excel-file-with-dcc-send-data-frame/53460/7
#     workbook=temp_writer.book
#     worksheet=temp_writer.sheets['sample_sheet_curated']
#     workbook,worksheet=update_excel_sheet_curated_sample_formatting(workbook,worksheet,store_panda)

#     worksheet.autofit()

#     worksheet=temp_writer.sheets['title_page']
#     worksheet.hide_gridlines()
#     worksheet.write('B2','Enjoy the curations :)')

#     temp_writer.save()
#     temp_data=output_stream.getvalue()

#     #ISSUE 38
#     #we want to expand the vocabulary on the fly. 
#     #this  forloop and the one below apply only to the "reject suggestions, create new" column
#     #for each non null reject suggetsion
#     #first, we want to compile a total list of new vocabulary so that we dont train 3x if there are 3 new species
#     new_vocab_dict=dict()
#     for i,new_vocabulary_word in enumerate(input_curation_value_ALL):
#         if new_vocabulary_word is not None:
#             try:
#                 new_vocab_dict[
#                     #notice that here we use the temp_header core vocabulary pattern: .split('.')[0]
#                     header_written_pair_children_ALL[i][0].split(': ')[0].split('.')[0]
#                 ].append(new_vocabulary_word)
#             except KeyError:
#                 new_vocab_dict[
#                     header_written_pair_children_ALL[i][0].split(': ')[0].split('.')[0]
#                 ]=[new_vocabulary_word]

#     #now, for each key in this dict, append to the corresponding panda in the conglomerate dict, then output it again
#     for temp_key in new_vocab_dict.keys():
        
#         training_success=requests.post(
#             base_url_api+'/trainvocabularyterms/',json={
#                 'header':temp_key,
#                 'new_vocabulary':new_vocab_dict[temp_key]
#             }
#         )
        
#         #no need for error check, already did that above

#     #this loop apply for every row in the curation table
#     #the purpose of this loop is to increment the use_count
#     for temp_tuple in header_replacement_list:
#         temp_header_core_vocabulary=temp_tuple[0].split('.')[0]
#         #for each thing to replace 
#         #get the corresponding panda
#         #from that, get the corresponding main string
#         #if there is more thjan one unique main string, raise an exception
#         #otherwise, 
#         temp_valid_string=temp_tuple[1].split(' AKA ')[0]
#         #AKA wont be in there if new vocabulary is added
#         if ' AKA ' in temp_tuple[1]:
#             temp_main_string=temp_tuple[1].split(' AKA ')[1]
#         else:
#             temp_main_string=temp_tuple[1].split(' AKA ')[0]

#         usecount_success=requests.post(
#             base_url_api+'/updateusecount/',json={
#                 'header':temp_header_core_vocabulary,
#                 'main_strings':temp_main_string
#             }
#         )

#     return [
#         None,dcc.send_bytes(temp_data,"binbase_sample_ingestion_form_curated.xlsx")
#     ]
