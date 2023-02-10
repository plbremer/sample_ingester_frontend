

import dash
from dash import dcc, html
import plotly.express as px
import dash_bootstrap_components as dbc

dash.register_page(__name__, path='/curate-and-download')

layout = html.Div(
    children=[
        html.Br(),
        html.Br(),
        dbc.Row(
            children=[
                dbc.Col(width=1),
                dbc.Col(
                    children=[
                        html.H3('Sample Descriptors'),
                        dbc.Checklist(
                            options=[
                                {"label": "Living Tissue, Organs (plasma, lung, etc.)", "value": 'living_tissue'},
                                {"label": "Living Cells (pure cells?)", "value": 'living_cells'},
                                {"label": "Raw Material (soil, water, etc.)", "value": 'raw_material'},
                            ],
                            #value=[1],
                            id="sample_checklist",
                        ),
                    ],
                    width=4
                ),
                dbc.Col(
                    children=[
                        html.H3('Study Descriptors'),
                    ],
                    width=4
                ),
                dbc.Col(width=2)
            ]
        )
    ],
)