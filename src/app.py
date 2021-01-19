from dash.dependencies import Input, Output, State
from lib import F1
from pathlib import Path

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd

path = Path(__file__).parent
PATH_TO_DATA = path.parent / 'data'

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

df = pd.read_csv(path / 'sakhir_timing.csv')

df_seasons = pd.read_csv(PATH_TO_DATA / 'seasons.csv')


fig = px.violin(df.loc[df['Constructor'] == 'mercedes'], y='LapTime',
        color='Driver', violinmode='overlay')

fig2 = px.box(df, x='Driver', y='LapTime', color='Driver')



app.layout = html.Div([

    html.Button(id='load-page', n_clicks=0, children='Load'),

    html.Div([

        dcc.Graph(
            id='example-graph',
            figure=fig
        ),

        html.Div([
            dcc.Dropdown(
                id='xaxis-column',
                options=[{'label':i, 'value':i} for i in df['Constructor'].unique()],
                value='Mercedes'
            ),
        ],style={'width': '48%', 'display':'inliine-block'}),

        dcc.Graph(
            id='Boxplot All Drivers',
            figure=fig2
        ),

        html.H6('Test Header'),

        html.Div(["Input: ", 
                    dcc.Input(id='Test Input', value='0', type='number')]),
        html.Br(),
        html.Div(id='Test Output')

    ], id='page-content', style={'display': 'none'})

])


@app.callback(
    Output(component_id='Test Output', component_property='children'),
    Input(component_id='Test Input', component_property='value')
)
def update_output_div(input_value):
    input_value = int(input_value) + 2
    return 'Output: ' + str(input_value)

@app.callback(
    Output('example-graph', 'figure'),
    Input('xaxis-column', 'value')
)
def update_graph(xaxis_column):
    dff = df.loc[df['Constructor'] == xaxis_column]
    fig = px.violin(dff, color='Driver', y='LapTime', violinmode='overlay')
    return fig

@app.callback(
    Output('page-content', 'style'),
    Input('load-page', 'n_clicks')
)
def update_page(n_clicks):
    if n_clicks % 2 == 1:
        return  {'display':'block'}
    else:
        return {'display':'none'}

if __name__ == '__main__':
    app.run_server(debug=True)