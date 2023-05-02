import dash
from dash import html, dcc,callback
import dash_bootstrap_components as dbc




local_stylesheet = {
    "href": "https://fonts.googleapis.com/css2?"
            "family=Lato:wght@400;700&display=swap",
    "rel": "stylesheet"
}

app = dash.Dash(__name__, use_pages=True, external_stylesheets=[dbc.themes.BOOTSTRAP, local_stylesheet ])

#custom ordering of navbar
my_page_link_list=[
    # dbc.NavLink('Start Here.', href='/download-and-resubmit',style = {'color': 'white','font-weight':'bold'},className='navlink-parker'),#,className='nav-link')),
    #dbc.NavLink('Curate and download', href='/curate-and-download',style = {'color': 'white','font-weight':'bold'}),
    dbc.NavLink('Return Home', href='/',style = {'color': 'white','font-weight':'bold'},className='navlink-parker'),#,className='nav-link')),
]

app.layout = html.Div(
    [
        #,storage_type='session'),
        dcc.Location('url'),
        dbc.NavbarSimple(
            children=[]+my_page_link_list,
            brand='Sample Metadata Standardizer',
            color='#1A3E68',
            brand_style = {'color': '#FFCD00'},
        ),
        # content of each page

        dash.page_container
    ]
)


if __name__ == "__main__":
    #app.run(debug=False, host='0.0.0.0')
    app.run(debug=True, host='0.0.0.0')