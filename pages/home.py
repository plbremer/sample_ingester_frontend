

import dash
from dash import html
import dash_bootstrap_components as dbc

dash.register_page(__name__, path='/')

layout = html.Div(
    children=[
        html.Br(),
        html.Br(),
        html.Br(),
        html.Br(),
        html.Br(),
        html.Br(),       
        html.Br(),
        html.Br(),
        dbc.Row(
            children=[
                dbc.Col(width=2),
                dbc.Col(
                    className='align-center',
                    children=[
                        #html.H3('text'),
                        html.Br(),
                        html.Div(
                            
                            children=[
                                dbc.Button(
                                    dbc.NavLink('GENERATE FORM', href='/generate-form',style = {'color': 'white','font-weight':'bold'},className='navlink-parker'),#,className='nav-link'))
                                ),
                            ],
                            style={'textAlign':'center'}
                        )
                       
                    ],
                    width=4,
                    #justify="center"
                ),
                dbc.Col(
                    children=[
                        html.Br(),
                        html.Div(
                            children=[
                                dbc.Button(
                                    dbc.NavLink('SUBMIT FORM', href='/submit-form',style = {'color': 'white','font-weight':'bold'},className='navlink-parker'),#,className='nav-link'))
                                ),
                            ],
                            style={'textAlign':'center'}
                        )

                    ],
                    width=4
                ),
                dbc.Col(width=2)
            ]
        )
    ],
)