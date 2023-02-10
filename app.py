import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

local_stylesheet = {
    "href": "https://fonts.googleapis.com/css2?"
            "family=Lato:wght@400;700&display=swap",
    "rel": "stylesheet"
}

app = dash.Dash(__name__, use_pages=True, external_stylesheets=[dbc.themes.BOOTSTRAP, local_stylesheet ])

#custom ordering of navbar
my_page_link_list=[
    dbc.NavLink('Download, resubmit', href='/download-and-resubmit',style = {'color': 'white','font-weight':'bold'},className='navlink-parker'),#,className='nav-link')),
    dbc.NavLink('Curate and download', href='/curate-and-download',style = {'color': 'white','font-weight':'bold'}),
]

app.layout = html.Div([
        dbc.NavbarSimple(
            # dbc.Container(
            children=[
                # html.A(
                #     # Use row and col to control vertical alignment of logo / brand
                #     dbc.Row([
                #         dbc.Col(html.Img(src='https://avatars.githubusercontent.com/u/45467465?s=200&v=4', height="50px")),
                #         dbc.Col(dbc.NavbarBrand(id="header", children="Binvestigate, a FiehnLab Production")),#, className="ms-2")),
                #         ], 
                #         align="center",
                #     ),
                #     href="https://fiehnlab.ucdavis.edu/",
                #     style={"textDecoration": "none"},
                # )
            # the earlier viersion that was alphabetized
            ]+my_page_link_list,
            brand='brand here',
            color='#1A3E68',
            brand_style = {'color': '#FFCD00'},
            #links_left=True,
            #style={"height": "100px"}, 
            # ), 
        ),
        #html.Hr(style={'color':'red','height':'50px'}),
        # content of each page
        dash.page_container
    ]
)


if __name__ == "__main__":
    #app.run(debug=False, host='0.0.0.0')
    app.run(debug=True)