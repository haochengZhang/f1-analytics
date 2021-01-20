from dash.dependencies import Input, Output, State
from lib import F1
from pathlib import Path

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd

#TODO: Move data injestion elsewhere
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

    html.H1(
        'Placeholder Header',
        style={
            'textAlign':'center'
        }
    ),
    html.Label([
        'Season:',
        dcc.Dropdown(
            id='seasons-dropdown',
            options=[{'label': i ,'value': i} for i in df_seasons['year'].sort_values(ascending=False)],
            placeholder='Select a season'),
    ]),

    html.Label([
        'Race:',
        dcc.Dropdown(
            id='races-dropdown',
            placeholder='Select a race')],
        style={'display':'none'},
        id='races-label'),

    html.Div([

        dcc.Graph(
            id='example-graph',
            figure=fig
        ),

        html.Div([
            dcc.Dropdown(
                id='xaxis-column',
                options=[{'label':i, 'value':i} for i in df['Constructor'].unique()],
                value='Mercedes',
                placeholder='Select a team'
            ),
        ],style={'width': '48%', 'display':'inliine-block'}),

        dcc.Graph(
            id='Boxplot All Drivers',
            figure=fig2
        ),

    ], id='page-content', style={'display': 'none'})

])

@app.callback(
    Output('example-graph', 'figure'),
    Input('xaxis-column', 'value')
)
def update_graph(xaxis_column):
    dff = df.loc[df['Constructor'] == xaxis_column]
    fig = px.violin(dff, color='Driver', y='LapTime', violinmode='overlay')
    return fig

@app.callback(
    Output('races-label', 'style'),
    Output('races-dropdown', 'options'),
    Input('seasons-dropdown', 'value')
)
def update_dropdowns(value):
    df_races = pd.read_csv(PATH_TO_DATA / 'races.csv')

    df_races = df_races.loc[df_races['year'] == value]
    options = [{'label':i, 'value':i} for i in df_races['name']]
    
    if value:
        return  [{'display':'block'}, options]
    else:
        return [{'display':'none'}, []]

@app.callback(
    Output('page-content', 'style'),
    Input('races-dropdown', 'value')
)
def update_page(value):
    #TODO: Load and update data source, update and rerender all graphs
    if value:
        return {'display':'block'}
    else:
        return {'display':'none'}

if __name__ == '__main__':
    app.run_server(debug=True)