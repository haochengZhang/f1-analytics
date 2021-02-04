from dash.dependencies import Input, Output, State
from lib import F1
from pathlib import Path

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

import json

#TODO: Move data injestion elsewhere
path = Path(__file__).parent
PATH_TO_DATA = path.parent / 'data'

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

df = pd.read_csv(path / 'sakhir_timing.csv')

df_seasons = pd.read_csv(PATH_TO_DATA / 'seasons.csv')

# fig = px.violin(df.loc[df['Constructor'] == 'mercedes'], y='LapTime',
#         color='Driver', violinmode='overlay')


fig = go.Figure()


fig2 = px.box(df, x='Driver', y='LapTime', color='Driver')



app.layout = html.Div([

    html.H1(
        'F1 Laptime Dashboard',
        style={
            'textAlign':'center'
        }
    ),
    html.Label([
        'Season:',
        dcc.Dropdown(
            id='seasons-dropdown',
            options=[
                {'label': i ,'value': i} for i in df_seasons['year'].sort_values(ascending=False)],
            placeholder='Select a season'),
    ], style={'width':'48%'}),

    html.Label([
        'Race:',
        dcc.Dropdown(
            id='races-dropdown',
            placeholder='Select a race')],
        style={'display':'none', 'width':'48%'},
        id='races-label'),

    html.Div([

        dcc.Graph(
            id='violin-drivers',
            figure=fig
        ),

        html.Div([
            dcc.Dropdown(
                id='xaxis-column',
                options=[
                    {'label':i, 'value':i} for i in df['Constructor'].unique()],
                value='',
                placeholder='Select a team'
            ),
        ],style={'width': '48%', 'display':'inliine-block'}),

        dcc.Graph(
            id='Boxplot All Drivers',
            figure=fig2
        ),

    ], id='page-content', style={'display': 'none'}),

    html.Div(id='race-data', style={'display':'none'}),
    html.Div(id='race-ids', style={'display':'none'}),

])
# TODO: Add comments to all callbacks
@app.callback(
    Output('violin-drivers', 'figure'),
    Input('xaxis-column', 'value'),
    prevent_initial_call=True
)
def update_graph(xaxis_column):
    # Creates violin plot comparing drivers of each constructor

    dff = df.loc[df['Constructor'] == xaxis_column]

    drivers = dff['Driver'].unique()
    
    # Check if theres only two drivers
    if len(drivers) == 2:
        fig = go.Figure()

        fig.add_trace(go.Violin(
            x = dff['Constructor'][ dff['Constructor'] == xaxis_column],
            y = dff['LapTime'][ dff['Driver'] == drivers[0]],
            side='negative',
            name=drivers[0],
            points=False
        ))

        fig.add_trace(go.Violin(
            x = dff['Constructor'][ dff['Constructor'] == xaxis_column],
            y = dff['LapTime'][ dff['Driver'] == drivers[1]],
            side='positive',
            name=drivers[1],
            points=False
        ))
    
    else:
        fig = px.violin(
            dff,
            color='Driver',
            y='LapTime',
            violinmode='overlay',
            points=False
        )

    fig.update_layout(
        title={
            'text': 'Driver Laptime Comparison',
            'x':0.5,
            'xanchor': 'center'
    })
    fig.update_traces()

    return fig

@app.callback(
    Output('races-label', 'style'),
    Output('races-dropdown', 'options'),
    Output('race-ids', 'children'),
    Input('seasons-dropdown', 'value')
)
def update_dropdowns(value):
    df_races = pd.read_csv(PATH_TO_DATA / 'races.csv')

    df_races = df_races.loc[df_races['year'] == value]
    options = [{'label':i, 'value':i} for i in df_races['name']]
    race_ids = df_races[['name', 'raceId']].set_index('name').to_json()
    
    if value:
        return  [{'display':'block', 'width':'48%'}, options, race_ids]
    else:
        return [{'display':'none', 'width':'48%'}, [], '']

@app.callback(
    Output('page-content', 'style'),
    Output('race-data','children'),
    Input('races-dropdown', 'value'),
    Input('race-ids', 'children')
)
def update_page(raceName, raceIds):
    #TODO: Load and update data source, update and rerender all graphs
    if raceName:
        raceId = pd.read_json(raceIds).to_dict()
        raceId = raceId['raceId'][raceName]

        df_laptimes = pd.read_csv(PATH_TO_DATA / 'lap_times.csv')
        df_laptimes = df_laptimes.loc[df_laptimes['raceId'] == raceId]

        df_drivers = pd.read_csv(PATH_TO_DATA / 'drivers.csv')
        df_drivers = df_drivers[['driverId', 'driverRef', 'surname']]

        idRef_map = df_drivers[
            ['driverId', 'driverRef']].set_index('driverId').to_dict()
        idRef_map = idRef_map['driverRef']

        idName_map = df_drivers[
            ['driverId', 'surname']].set_index('driverId').to_dict()
        idName_map = idName_map['surname']

        df_laptimes['driverRef'] = df_laptimes['driverId'].map(idRef_map)
        df_laptimes['surname'] = df_laptimes['driverId'].map(idName_map)

        

        return [{'display':'block'}, df_laptimes.to_json()]
    else:
        return [{'display':'none'},[]]

if __name__ == '__main__':
    app.run_server(debug=True)