import env

import dash
from dash import dcc
from dash import html

import plotly.express as px

import mariadb

import pandas as pd


app = dash.Dash(__name__)

try:
    conn = mariadb.connect(
        user=env.USER,
        password=env.PASSWORD,
        host=env.SERVER,
        port=env.PORT,
        database=env.DATABASE
    )
except mariadb.Error as e:
    print(f'Error connecting to MariaDB Platform: {e}')

df = pd.read_sql('SELECT created, CAST(state as INT) as state FROM states WHERE entity_id = \'sensor.dht22_humidity\' LIMIT 100', conn, index_col='created');

print(df.head())

fig = px.line(df)

app.layout = html.Div(children=[
    html.H1(children='Test Site'),
    dcc.Graph(id='example-graph', figure=fig)
])

if __name__ == '__main__':
    app.run_server(debug=True)