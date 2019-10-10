import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
# import plot_MoDB as pmdb
import modb



external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

gc = modb.database('GC')

app.layout = html.Div([
    html.Div([
        dcc.Markdown('''
            ### Search the General Conference Archives
            ***
            The [Church of Jesus Christ of Latter-Day Saints](https://www.churchofjesuschrist.org/?lang=eng) 
            (formerly known as Mormons)
            has a biannnual conference known as General Conference. It is the primary 
            vehicle through which the leadership of the LDS Church provides encouragement, 
            moral guidance and correction, and doctrinal exposition. 

            I made this little app to help me investigate trends in how the church leadership speaks
            to the members, and how those trends have changed (or remained the same) over time.

            ** HOW TO USE THE APP: **
            * To see the probability of given word/phrase over time, just add a search term in the search box and hit return.
            You can keep adding search terms to see how they compare.
            * You can also add/remove previously searched terms using the pulldown menu. 
            * You can adjust how smooth the plot is with the smoothing slider. 

            I hope you find this little project useful. 
            ***
            #### Select your search term(s)
            '''),
        dcc.Input(
            id='input', 
            value='faith',
            placeholder='search term',
            type='text',
            n_submit=1),
        dcc.Dropdown(
            id='dropdown',
            options=[],
            value=[],
            multi=True
        )
    ]),
    html.Div([
        dcc.Markdown('''
            #### Set line smoothing
            '''),
        dcc.Slider(
            id='slider',
            min=0,
            max=4,
            step=1,
            value=1,
            marks={i: '{}'.format(i) for i in range(0,5)})
        ], style={'marginTop':50, 'marginLeft':90, 'marginRight':300, 'marginBottom':25}),
    html.Div([
        dcc.Markdown('''
            #### Hits vs Probability
            You can select hits to see the raw number of hits for your search term(s). However, some years had more
            words overall than others; it is sometimes more informative to see the probability (hits divided by total # of words)
            of your search term(s).

            Hint: If you choose hits, it makes sense to set the smoothing slider to 0.
            '''),
        dcc.RadioItems(
            options=[
                {'label': 'Hits', 'value': 'Hits'},
                {'label': 'Probability', 'value': 'Probability'},
                ],
            value='Probability',
            id='radio')  
        ],style={'marginTop':50, 'marginLeft':90,'marginRight':300}),
    html.Div([
    dcc.Graph(
        id='output-graph', 
        style={"width": "80%", "display": "inline-block","height":600})
    ]),
], style={'marginTop':50, 'marginLeft':50, 'marginRight':50, 'marginBottom':50})





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
    fig.fig.update_layout(showlegend=True)
    return fig.fig


if __name__ == '__main__':
    app.run_server(debug=True)