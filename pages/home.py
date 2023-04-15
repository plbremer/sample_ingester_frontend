

import dash
from dash import html
import dash_bootstrap_components as dbc

dash.register_page(__name__, path='/')

layout = html.Div(
    children=[
        html.Br(),
        html.Br(),
        dbc.Row(
            children=[
                dbc.Col(width=2),
                dbc.Col(
                    children=[
                        html.H3('text'),
                        html.Br(),
                        dbc.Button(
                            dbc.NavLink('I want to generate a form', href='/generate-form',style = {'color': 'white','font-weight':'bold'},className='navlink-parker'),#,className='nav-link'))
                        ),
                    ],
                    width=4
                ),
                dbc.Col(
                    children=[
                        html.Br(),
                        dbc.Button(
                            dbc.NavLink('I want to submit a form', href='/submit-form',style = {'color': 'white','font-weight':'bold'},className='navlink-parker'),#,className='nav-link'))
                        ),
                    ],
                    width=4
                ),
                dbc.Col(width=2)
            ]
        )
    ],
)