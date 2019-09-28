import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import plotly_express
import plot_MoDB as pmdb
import pandas as pd


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

app.layout = html.Div([
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

        To use the app, just add a search term in the "ADD OPTION" box and then click the button.
        Your search term will now appear in the pulldown menu below. Select your search term(s)
        and watch as the chart updates. 

        I hope you find this little project useful. 
        ***
        '''),
    dcc.Input(id='input', value=''),
    html.Button('Add Option', id='submit'),
    html.Div(id='confirm'),
    dcc.Dropdown(
        id='dropdown',
        options=[
            {'label': 'jesus', 'value': 'jesus'},
            {'label': 'faith', 'value': 'faith'},
            {'label': 'joseph', 'value': 'joseph'},
        ],
        value=['jesus','faith'],
        multi=True
    ),
    dcc.Graph(id='output-graph', style={"width": "80%", "display": "inline-block"}),
], style={'marginTop':50, 'marginLeft':50, 'marginRight':50, 'marginBottom':50})

# First callback for selecting the search terms
@app.callback([
    Output('dropdown', 'options'),
    Output('confirm', 'children')],
    [Input('submit', 'n_clicks')],
    [State(component_id='input', component_property='value'),
     State(component_id='dropdown', component_property='options')]
)
def select_terms(n_clicks,new_value,current_options):
    if not n_clicks:
        raise PreventUpdate
    current_options.append({'label': new_value.lower(), 'value': new_value.lower()})
    confirmation='"' + new_value.lower() + '" added as a new search option.'
    return current_options, confirmation


@app.callback(
    Output('output-graph','figure'),
    [Input('dropdown','value')]
)
def update_graph(input_strings):
    if len(input_strings)==0:
        return {}
    years=range(1942,2020)
    for i,s in enumerate(input_strings):
        # get the string frequencies for the specified years
        pbs = pmdb.get_probs_for_years(years,s)

        # add to a single dataframe
        if i==0:
            p1 = pd.DataFrame(data={'Years':years,'Probability':pbs, 'string':list([s]*len(years))})
        else:
            p1 = p1.append(pd.DataFrame(data={'Years':years,'Probability':pbs, 'string':list([s]*len(years))}))

    return plotly_express.line(p1,
        x = 'Years',
        y = 'Probability',
        line_group = 'string',
        color = 'string')



if __name__ == '__main__':
    app.run_server(debug=True)