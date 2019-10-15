import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import modb



external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

gc = modb.database('GC')



def demo_explanation():
    # Markdown files
    with open("info.md", "r") as file:
        demo_md = file.read()

    return html.Div(
        html.Div([dcc.Markdown(demo_md, className="markdown")]),
        style={"margin": "10px","color":"white"},
    )





def instructions():
    return html.P(
        children=[
            """
    Search a database of LDS General Conference archives (1942-2019)
    Instructions:
    - Enter a search term and hit return
    - Keep adding search terms to see how they compare
    - Add/remove previously searched terms using the pulldown menu
    - Display the raw number of hits or the probability of the word for each year
    - Use the slider to adjust the smoothing of the plot
    """
        ],
        className="instructions-sidebar",
    )

app.layout = html.Div(
    children=[
        html.Div(
            [   

                html.Div([
                    html.A(
                        html.Button(
                            "View on GitHub",
                            className="git_button",
                        ),
                        href='https://github.com/danielkentwood/SearchMoDB',
                    ),
                    html.Img(className="logo", src=app.get_asset_url("GitHub-Mark-Light-64px.png")),
                ],
                # style={"display":"inline-block"}
                ),


                    

                # html.Div(
                #     html.A(
                #         html.Button(
                #             "View on GitHub",
                #         ),
                #         href='https://github.com/danielkentwood/SearchMoDB',
                #     ),
                #     style={"margin-top":"15px","display":"inline-block"}
                # ),
                # html.Div(
                #     html.Img(className="logo", src=app.get_asset_url("GitHub-Mark-Light-64px.png")),
                # ),


                html.H1(
                    children="Search MoDB",
                    style={"margin-top":"60px"}
                ),
                instructions(),
                html.Div(
                    [
                        html.Button(
                            "LEARN MORE",
                            className="button_instruction",
                            id="learn-more-button",
                        ),
                    ],
                    className="mobile_buttons",   
                ),
                html.Div(
                    # Empty child function for the callback
                    html.Div(id="demo-explanation", children=[])
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.Label("Add new search term"),
                                dcc.Input(
                                    id='input', 
                                    value='faith',
                                    placeholder='search term',
                                    type='text',
                                    n_submit=1),
                            ]       
                        ),
                        html.Div(
                            [
                                html.Label("Add/remove previous search term(s)"),
                            ],
                        ),
                        html.Div(
                            [
                                dcc.Dropdown(
                                    id='dropdown',
                                    options=[],
                                    value=[],
                                    multi=True)
                            ], style={"margin-left": "9%","margin-right":"40%","margin-top":"4px"},
                        ),
                    ],
                    className="mobile_forms",
                ),
                html.Div(
                    [
                        html.Label("Hits vs Probability"),
                        dcc.RadioItems(
                            options=[
                                {'label': 'Hits', 'value': 'Hits'},
                                {'label': 'Probability', 'value': 'Probability'},
                                ],
                            value='Probability',
                            id='radio',
                            labelStyle={"display": "inline-block","color":"white"},
                            style={"margin-top": "-18px"},
                        ), 
                    ],
                    className="radio_items",
                ),
                html.Div(
                    [
                        html.Label("Set line smoothing"),
                    ],
                ),
                html.Div(
                    [
                        dcc.Slider(
                            id='slider',
                            min=0,
                            max=4,
                            step=1,
                            value=1,
                            marks={i: '{}'.format(i) for i in range(0,5)},
                        ),
                    ], style={"margin-left": "10%","margin-right":"30%"},
                ),
            ],
            className="four columns instruction",
        ),
        html.Div(
            [
                dcc.Graph(
                    id='output-graph', 
                    style={"width": "95%", "display": "inline-block","height":600}
                ),
            ],
            className="eight columns result",
            style={"backgroundColor":"#f8f2f2"}
        ),
    ],
    className="row twelve columns",
    style={"backgroundColor":"#f8f2f2"},
)

@app.callback([
    Output('dropdown', 'options'),
    Output('dropdown','value')],
    [Input('input', 'n_submit')],
    [State('input', 'value'),
     State('dropdown', 'options'),
     State('dropdown', 'value')]
)
def select_terms(click,new_value,current_options,current_values):
    for o in current_options:
        if new_value in list(o.values()):
            if new_value in current_values:
                raise PreventUpdate
            else:
                current_values.append(new_value.lower())
                return current_options, current_values

    current_options.append({'label': new_value.lower(), 'value': new_value.lower()})
    current_values.append(new_value.lower())
    return current_options, current_values



@app.callback(
    Output('output-graph','figure'),
    [Input('dropdown','value'),
    Input('slider','value'),
    Input('radio','value')]
)
def update_graph(input_strings,slider_val,radio_val):
    fig = modb.figure()
    fig.set_smoothing(slider_val)
    for i,s in enumerate(input_strings):
        if radio_val=='Probability':
            # get the string frequencies for the specified years
            y_data = gc.string_probability(s)
        else:
            y_data = gc.string_hits(s)

        fig.add_trace(gc.years,y_data,s)

    fig.set_axes(radio_val)
    fig.fig.update_layout(
        showlegend=True, 
        paper_bgcolor='#f8f2f2'
    )
    return fig.fig


@app.callback(
    [Output("demo-explanation", "children"), Output("learn-more-button", "children")],
    [Input("learn-more-button", "n_clicks")],
)
def learn_more(n_clicks):
    if n_clicks == None:
        n_clicks = 0
    if (n_clicks % 2) == 1:
        n_clicks += 1
        return (
            html.Div(
                className="demo_container",
                style={"margin-bottom": "30px"},
                children=[demo_explanation()],
            ),
            "Close",
        )

    n_clicks += 1
    return (html.Div(), "Learn More")



if __name__ == '__main__':
    app.run_server(debug=True)