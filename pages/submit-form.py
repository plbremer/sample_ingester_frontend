from dash import dcc, html,dash_table,callback, ctx,MATCH,ALL


import dash


dash.register_page(__name__, path='/submit-form')


layout = html.Div(
    children=[
        html.H6('hi')
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
    ],
)