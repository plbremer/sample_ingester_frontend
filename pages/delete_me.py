import dash_mantine_components as dmc
from dash import html, Output, Input, State, ctx, callback,dcc

import dash
import dash_bootstrap_components as dbc

from time import time

min_step = 0
max_step = 3
active = 0


local_stylesheet = {
    "href": "https://fonts.googleapis.com/css2?"
            "family=Lato:wght@400;700&display=swap",
    "rel": "stylesheet"
}

app = dash.Dash(__name__, use_pages=False, external_stylesheets=[dbc.themes.BOOTSTRAP, local_stylesheet ])

app.layout =html.Div(
    [
        dmc.Stepper(
            id="stepper-basic-usage",
            active=active,
            breakpoint="sm",
            children=[
                dmc.StepperStep(
                    label="First step",
                    description="Create an account",
                    children=[

                        dmc.Text("0th content", align="center"),


                    ]
                ),
                dmc.StepperStep(
                    label="Second step",
                    description="Verify email",
                    children=dmc.Text("1th content", align="center"),
                ),
                dmc.StepperStep(
                    label="Final step",
                    description="Get full access",
                    children=dmc.Text(
                        "2th content", align="center"
                    ),
                ),

            #     dmc.StepperStep(
            #         id={"type":"my_stepper","index":i},
            #         description=f"step {i}",
            #         children=dmc.Text(f"we are are on step {i}")
            #     ) for i in range(0,4)
            # ]+[
                dmc.StepperCompleted(
                    children=dmc.Text(
                        "Completed, click back button to get to previous step",
                        align="center",
                    )
                ),
            ],
        ),
        dmc.Group(
            position="center",
            mt="xl",
            children=[
                dmc.Button("Back", id="back-basic-usage", variant="default"),
                dmc.Button("Next step", id="next-basic-usage"),
            ],
        ),
    ]
)


@callback(
    Output("stepper-basic-usage", "active"),
    Output("stepper-basic-usage","children"),
    Input("back-basic-usage", "n_clicks"),
    Input("next-basic-usage", "n_clicks"),
    State("stepper-basic-usage", "active"),
    State("stepper-basic-usage", "children"),
    prevent_initial_call=True,
)
def update(back, next_, current,my_children):
    print('-------')
    print(ctx.triggered_id)
    print(current)
    button_id = ctx.triggered_id
    step = current if current is not None else active
    if button_id == "back-basic-usage":
        step = step - 1 if step > min_step else step
    else:
        step = step + 1 if step < max_step else step

    print(step)
    
    #output_children=my_children
    current_time=time()
    if current<3:
        my_children[current]=dmc.StepperStep(
                        label='this_should_be_dynamic',
                        description="this_should_be_tynamic",
                        children=dmc.Text(
                            f"the previous time was {current_time}", align="center"
                        ),
                    )
    else:
        my_children[current]=dmc.StepperCompleted(
                    children=dmc.Text(
                        "Completed, click back button to get to previous step",
                        align="center",
                    )
                ),      

    print('about to output')
    return step,my_children


if __name__ == "__main__":
    #app.run(debug=False, host='0.0.0.0')
    app.run(debug=True, host='0.0.0.0')