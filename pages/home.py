

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
                        html.H3('Any text or whatever'),
                        html.Br(),
                        dbc.Button(
                            dbc.NavLink('I want to generate a form', href='/generate-form',style = {'color': 'white','font-weight':'bold'},className='navlink-parker'),#,className='nav-link'))
                        ),
                    ],
                    width=8
                ),
                dbc.Col(width=2)
            ]
        )
    ],
)