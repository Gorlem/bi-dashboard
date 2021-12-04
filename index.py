import dash
from dash import dcc
from dash import html
from dash.dependencies import Output, Input
from dash.exceptions import PreventUpdate

import plotly.express as px

import pandas as pd

import db
import mappings

app = dash.Dash(__name__)

illuminance = db.illuminance()

weekdays = {
    0: 0,
    1: 0,
    2: 0,
    3: 0,
    4: 0,
    5: 0,
    6: 0,
}

start = None

for row in illuminance.itertuples():
    if start is None:
        if row.lux > 100:
            start = row.Index
    else:
        if row.lux < 100:
            end = row.Index

            weekdays[end.weekday()] += (end - start).seconds

            start = None

common_days = pd.Series(weekdays)
common_days = common_days.rename({ 0: 'Montag', 1: 'Dienstag', 2: 'Mittwoch', 3: 'Donnerstag', 4: 'Freitag', 5:'Samstag', 6:'Sonntag' })
common_days = common_days / 60 / 60
common_days = common_days.sort_values(ascending=False).head(n=3)

print(common_days)

illuminance_fig = px.bar(common_days, height=100, labels={'value': 'Stunden'})
illuminance_fig.update_layout(
    margin={ 'l': 0, 'r': 0, 't': 0, 'b': 0 },
    showlegend=False,
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    bargap=0,
    xaxis_title=None,
)

humidity = db.humidity_comparison()
print(humidity.head())
humidity_fig = px.line(humidity, height=300)
humidity_fig.update_layout(margin={ 'l': 0, 'r': 0, 't': 0, 'b': 0 })

wifi = db.wifi()
print(wifi.head())
wifi_fig = px.line(wifi, height=300)
wifi_fig.update_layout(margin={ 'l': 0, 'r': 0, 't': 0, 'b': 0 })

amounts = db.amounts()
mappings.mapping(amounts)
counts_fig = px.sunburst(amounts, path=['*', 'type', 'name'], values='amount', maxdepth=2, height=300)
counts_fig.update_layout(margin={ 'l': 0, 'r': 0, 't': 0, 'b': 0 })

temps = db.temperature()
current_temp = temps.iloc[0]['state']
temp_fig = px.line(temps, height=100)
temp_fig.update_layout(
    margin={ 'l': 0, 'r': 0, 't': 0, 'b': 0 },
    showlegend=False,
    yaxis_visible=False,
    xaxis_visible=False,
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
)
temp_fig.update_traces(line_color='hsl(48, 100%, 29%)')

hum = db.humidity()
current_hum = hum.iloc[0]['state']
hum_fig = px.line(hum, height=50)
hum_fig.update_layout(
    margin={ 'l': 0, 'r': 0, 't': 0, 'b': 0 },
    showlegend=False,
    yaxis_visible=False,
    xaxis_visible=False,
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
)

co2 = db.co2()
current_co2 = co2.iloc[0]['state']
co2_fig = px.line(co2, height=50)
co2_fig.update_layout(
    margin={ 'l': 0, 'r': 0, 't': 0, 'b': 0 },
    showlegend=False,
    yaxis_visible=False,
    xaxis_visible=False,
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
)

tvoc = db.tvoc()
current_tvoc = tvoc.iloc[0]['state']
tvoc_fig = px.line(tvoc, height=80, title='TVOC')
tvoc_fig.update_layout(
    margin={ 'l': 0, 'r': 0, 't': 30, 'b': 0 },
    showlegend=False,
    yaxis_visible=False,
    xaxis_visible=False,
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
)


app.layout = html.Div(children=[
    html.Nav(className='navbar is-primary', children=[
        html.Div(className='navbar-brand', children=[
            html.P(className='navbar-item', children='BI Dashboard')
        ])
    ]),
    html.Div(className='section', children=[
        html.Nav(className='level', children=[
            html.Div(className='level-item has-text-centered', children=[
                html.Div(children=[
                    html.P(className='heading', children='Lorem'),
                    html.P(className='title', children='1337'),
                ]),
            ]),
            html.Div(className='level-item has-text-centered', children=[
                html.Div(children=[
                    html.P(className='heading', children='Ipsum'),
                    html.P(className='title', children='420'),
                ]),
            ]),
            html.Div(className='level-item has-text-centered', children=[
                html.Div(children=[
                    html.P(className='heading', children='Est'),
                    html.P(className='title', children='12345'),
                ]),
            ]),
        ]),
    ]),
    html.Div(className='section', children=[
        html.Div(className='tile is-ancestor', children=[
            html.Div(className='tile is-parent is-vertical', children=[
                html.Div(className='tile box', children=[
                    html.Div(className='tile is-child notification is-warning mr-4', children=[
                        html.H4(className='title is-4', children=f'Temperatur {current_temp}°C', id='temperature'),
                        dcc.Graph(id='temp-graph', figure=temp_fig, config=dict(displayModeBar=False)),
                    ]),
                    html.Div(className='tile is-vertical ml-4', children=[
                        html.Div(className='tile notification', children=[
                            html.H4(className='tile is-child title is-4', children=f'Luftfeuchtigkeit'),
                            dcc.Graph(className='tile is-child', id='hum-graph', figure=hum_fig, config=dict(displayModeBar=False)),
                        ]),
                        html.Div(className='tile is-child notification', children=[
                            html.H6(className='title is-6', children=f'CO2'),
                            dcc.Graph(id='co2-graph', figure=co2_fig, config=dict(displayModeBar=False)),
                        ]),
                        html.Div(className='tile is-child notification', children=[
                            dcc.Graph(id='tvoc-graph', figure=tvoc_fig, config=dict(displayModeBar=False)),
                        ]),
                    ]),
                ]),
                html.Div(className='tile is-child card', children=[
                    html.Div(className='card-content', children=[
                        dcc.Graph(id='wifi-graph', figure=wifi_fig),
                    ])
                ]),
            ]),
            html.Div(className='tile is-parent is-vertical', children=[
                html.Div(className='tile is-child card', children=[
                    html.Header(className='card-header', children=[
                        html.P(className='card-header-title', children='Vergleich Feuchtigkeitssensoren')
                    ]),
                    html.Div(className='card-content', children=[
                        dcc.Graph(id='humidity-graph', figure=humidity_fig),
                    ])
                ]),
                html.Div(className='tile'),
            ]),
            html.Div(className='tile is-2 is-vertical is-parent', children=[
                html.Div(className='tile is-child box', children=[
                    html.H4(className='title is-4', children='Datenmenge nach Sensor'),
                    dcc.Graph(id='counts-graph', figure=counts_fig),
                ]),
                html.Div(className='tile is-child box', children=[
                    html.H4(className='title is-4', children='Raumnutzung'),
                    dcc.Graph(id='illuminance-graph', figure=illuminance_fig, config=dict(displayModeBar=False)),
                ]),
                html.Div(className='tile is-child box', children=[
                    html.H4(className='title is-4', children=[
                        'Prozentzahl ',
                        html.Span(className='tag', children='Tag')
                    ]),
                    html.Progress(className='progress', value='20', max='100', children='20%')
                ]),
                html.Div(className='tile is-child notification', children=[
                    # html.H4(className='title is-4', children='⚠ Warnung'),
                    'Luftfeuchtigkeit is im normalen Bereich'
                ]),
                html.Div(className='tile'),
            ]),
        ]),
    ]),
    
    
    # dcc.Interval(id='interval', interval=1000, n_intervals=0) # 1s
])

@app.callback(
    Output('illuminance-graph', 'figure'),
    Input('interval', 'n_intervals')
)
def update_graph(n):
    global illuminance

    last = illuminance.index.max()
    formatted = last.isoformat()

    new = pd.read_sql('SELECT created, CAST(state as FLOAT) as state FROM states WHERE entity_id = \'sensor.bh1750_illuminance_2\' AND created > \'' + formatted + '\' ORDER BY created DESC LIMIT 10', engine, index_col='created')

    if new.empty:
        raise PreventUpdate

    print(new.head())

    illuminance = new.append(illuminance)

    print(illuminance.tail())

    return px.line(illuminance)

if __name__ == '__main__':
    app.run_server(debug=True)