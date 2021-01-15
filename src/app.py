import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# assume you have a "long-form" data frame
# see https://plotly.com/python/px-arguments/ for more options
df = pd.read_csv(
        'C:\\Users\\hzhang\\Documents\\Work\\F1\\src\\sakhir_timing.csv')

fig = px.violin(df.loc[df['Constructor'] == 'mercedes'], y='LapTime',
        color='Driver', violinmode='overlay')

fig2 = px.box(df, x='Driver', y='LapTime', color='Driver')

app.layout = html.Div(children=[
    html.H1(children='Hello Dash'),

    html.Div(children='''
        Dash: A web application framework for Python.
    '''),

    dcc.Graph(
        id='example-graph',
        figure=fig
    ),

    dcc.Graph(
        id='Boxplot All Drivers',
        figure=fig2
    )

])

if __name__ == '__main__':
    app.run_server(debug=True)