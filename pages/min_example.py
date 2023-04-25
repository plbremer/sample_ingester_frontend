import dash
from dash import dcc, html,dash_table,callback
#import dash_mantine_components as dmc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State


app = dash.Dash(__name__)

app.layout = html.Div(
    children=[
        html.Div(
            id='datatable_div',
            children=[]
        ),
        html.Br(),
        html.Br(),
        html.Div(
            children=[
                html.Div(
                    dbc.Button(
                        'Add column',
                        id='button_column_add',
                    ),
                    className="d-grid gap-2 col-6 mx-auto",
                ),
            ]
        )
    ]
)

@callback(
    [
        Output(component_id='datatable_div', component_property='children'),
    ],
    [
        Input(component_id='button_column_add', component_property="n_clicks"),
    ],
    prevent_initial_call=True
)
def update(button_column_add_n_clicks):
    

    total_columns=[
        {
            'name':'long name to make this a little faster',
            'id':str(i)
        } for i in range(button_column_add_n_clicks)
    ]

    total_data=[
        {
            temp_col['id']:'nonsense data' for temp_col in total_columns
        }
    ]
    
    
    output_children=[
        dbc.Row(
            children=[
                dbc.Col(width=1),
                dbc.Col(
                    children=[
                        #dmc.Center(
                        html.Div(
                            children=[
                                dash_table.DataTable(
                                    id='dt_for_preview',
                                    columns=total_columns,
                                    data=total_data,
                                    style_cell={
                                        'fontSize': 17,
                                        'padding': '8px',
                                        'textAlign': 'center',
                                        
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
                                        'color':'rgb(211,211,211)',
                                        'font-style':'italic'
                                    },
                                    style_table={
                                        'overflowX': 'scroll'
                                    },
                                    page_action='native',
                                    page_size=3,
                                    fill_width=False,
                                    # virtualization=True
                                )
                            ],
                        )
                    ],
                    width=10
                ),
                dbc.Col(width=1)
            ]
        ),        
    ]


    return [output_children]



if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')