import locale
import datetime

import dash
from dash import dcc
from dash import html
from dash.dependencies import Output, Input
from dash.exceptions import PreventUpdate

import plotly.express as px
import plotly.graph_objects as go

import pandas as pd
from sqlalchemy.sql import annotation

import db
import mappings

locale.setlocale(locale.LC_ALL, 'de-DE')

app = dash.Dash(__name__)

lux_inside = db.lux_inside()
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

for row in lux_inside.itertuples():
    if start is None:
        if row.lux_inside > 100:
            start = row.Index
    else:
        if row.lux_inside < 100:
            end = row.Index

            weekdays[end.weekday()] += (end - start).seconds

            start = None

common_days = pd.Series(weekdays)
amount_of_weekdays = db.amount_of_weekdays()
common_days = common_days / amount_of_weekdays['count']
common_days = common_days.rename({ 0: 'Montag', 1: 'Dienstag', 2: 'Mittwoch', 3: 'Donnerstag', 4: 'Freitag', 5:'Samstag', 6:'Sonntag' })
common_days = common_days / 60 / 60
common_days = common_days.sort_values(ascending=False).head(n=3)

weekdays_fig = px.bar(common_days, height=100, labels={'value': 'Stunden'})
weekdays_fig.update_layout(
    margin={ 'l': 0, 'r': 0, 't': 0, 'b': 0 },
    showlegend=False,
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    bargap=0,
    xaxis_title=None,
)

lux_outside = db.lux_outside()
all_switch_power = db.all_switch_power()

lux_comp = lux_inside.resample('15T').mean().pad().join(lux_outside.resample('15T').mean().pad()).join(all_switch_power.resample('15T').mean().pad())
print(lux_comp)
lux_fig = px.scatter(lux_comp, y='lux_inside', x='lux_outside', color='power', height=300, labels={
    'lux_outside': 'Lichtstärke Außen [lux]',
    'lux_inside': 'Lichtstärke Innen [lux]',
    'power': 'Leistung [W]',
})
lux_fig.update_layout(
    margin={ 'l': 0, 'r': 0, 't': 0, 'b': 0 },
)

lux_fig.add_hline(y=100, line_dash='dot', annotation_text='Grenzwert Raumnutzung', annotation_position='bottom right')

humidity = db.humidity_comparison()
print(humidity.head())
humidity_fig = px.line(humidity, height=300)
humidity_fig.update_layout(margin={ 'l': 0, 'r': 0, 't': 0, 'b': 0 })

wifi = db.wifi()
print(wifi.head())
wifi_fig = px.line(wifi, height=300, labels={'value': 'Signalstäre [dB]', 'variable': 'Sensoren'})
wifi_fig.update_layout(
    margin={ 'l': 0, 'r': 0, 't': 0, 'b': 0 },
    xaxis_title=None,
)
wifi_fig.add_hrect(y0=-50, y1=-65, line_width=0, fillcolor="orange", opacity=0.25, annotation_text="Schwaches Signal", annotation_position="top right")

amounts = db.amounts()
mappings.mapping(amounts)
counts_fig = px.sunburst(amounts[amounts.type != 'Unknown'], path=['*', 'type', 'name'], values='amount', maxdepth=2, height=250)
counts_fig.update_layout(margin={ 'l': 0, 'r': 0, 't': 0, 'b': 0 }, hovermode=False)

temps = db.temperature()
current_temp = temps.state[0]
print(current_temp)
print(type(current_temp))
temp_fig = px.line(temps.resample('30T').mean().pad(), height=150)
temp_fig.update_layout(
    margin={ 'l': 10, 'r': 0, 't': 0, 'b': 20 },
    showlegend=False,
    xaxis_title=None,
    yaxis_title=None,
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
)

hum = db.humidity()
current_hum = hum.state[0]
hum_fig = px.line(hum.resample('30T').mean().pad(), height=70)
hum_fig.update_layout(
    margin={ 'l': 10, 'r': 0, 't': 0, 'b': 20 },
    showlegend=False,
    xaxis_title=None,
    yaxis_title=None,
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
)
hum_status = 'success' if 40 <= current_hum <= 70 else 'warning' if 30 <= current_hum <= 70 else 'danger'

co2 = db.co2()
current_co2 = co2.state[0]
co2_fig = px.line(co2.resample('30T').mean().pad(), height=70)
co2_fig.update_layout(
    margin={ 'l': 10, 'r': 0, 't': 0, 'b': 20 },
    showlegend=False,
    xaxis_title=None,
    yaxis_title=None,
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
)
co2_status = 'success' if current_co2 <= 1000 else 'warning' if current_co2 <= 2000 else 'danger'

tvoc = db.tvoc()
current_tvoc = tvoc.state[0]
tvoc_fig = px.line(tvoc.resample('30T').mean().pad(), height=70)
tvoc_fig.update_layout(
    margin={ 'l': 10, 'r': 0, 't': 0, 'b': 20 },
    showlegend=False,
    xaxis_title=None,
    yaxis_title=None,
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
)
tvoc_status = 'success' if current_tvoc <= 3 else 'warning' if current_tvoc <= 25 else 'danger'

if hum_status == 'success' and co2_status == 'success' and tvoc_status == 'success':
    overall_climate = 'Gutes Raumklima'
else:
    overall_climate = 'Schlechtes Raumklima'

climate_messages = []

if hum_status != 'success':
    climate_messages.append('Luftfeuchtigkeit nicht im optimalen Bereich von 40% - 60%.')

if co2_status == 'warning':
    climate_messages.append('CO2-Konzentration zu hoch. Bitte lüften.')
if co2_status == 'danger':
    climate_messages.append('CO2-Konzentration inakzeptabel. Umgehend den Raum belüften.')

if tvoc_status == 'warning':
    climate_messages.append('TVOC-Konzentration zu hoch. Bitte lüften.')
if tvoc_status == 'danger':
    climate_messages.append('TVOC-Konzentration bedenklich. Gesundheitliche Folgen möglich.')

switch_power = db.switch_power()
switch_power_fig = go.Figure(
    go.Indicator(
        mode = 'gauge+number+delta',
        value = switch_power.state[0],
        gauge_axis_range = [None, 170],
        delta_reference = switch_power.state.mean()
    ),
)
switch_power_fig.update_layout(
    margin={ 'l': 30, 'r': 30, 't': 0, 'b': 0 },
    height=150,
    width=250,
)

switch_current = db.switch_current()
switch_current_fig = go.Figure(
    go.Indicator(
        mode = 'gauge+number+delta',
        value = switch_current.state[0],
        gauge_axis_range = [None, 1],
        delta_reference = switch_current.state.mean()
    ),
)
switch_current_fig.update_layout(
    margin={ 'l': 30, 'r': 30, 't': 0, 'b': 0 },
    height=150,
    width=250,
)

daily_power = db.daily_wlan_switch_power()


date_range = db.date_range()
print(date_range)

app.layout = html.Div(children=[
    html.Nav(className='navbar is-dark has-shadow', children=[
        html.Div(className='navbar-brand', children=[
            html.Div(className='navbar-item', children=[
                html.P(className='is-size-4', children='Business Intelligence Dashboard'),
            ]),
        ]),
        html.Div(className='navbar-end', children=[
            html.P(className='navbar-item', children=[
                'Daten von ',
                html.Span(className='tag mx-1', children=date_range.first_date[0].strftime('%c')),
                ' bis ',
                html.Span(className='tag mx-1', children=date_range.last_date[0].strftime('%c')),
            ]),
        ]),
    ]),
    html.Div(className='section py-4', children=[
        html.Div(className='tile is-ancestor', children=[
            html.Div(className='tile is-vertical is-parent', children=[
                html.Div(className='tile is-child', children=[
                    html.Nav(className='level', children=[
                        html.Div(className='level-item has-text-centered', children=[
                            html.Div(children=[
                                html.Div(className='is-inline-block', children=[
                                    dcc.Graph(figure=switch_power_fig, config=dict(locale='de')),
                                ]),
                                html.P(className='heading', children='Leistung WLAN Switch'),
                            ]),
                        ]),
                        html.Div(className='level-item has-text-centered', children=[
                            html.Div(children=[
                                html.H3(className='title is-3', children='123'),
                                html.P(className='heading', children='Verbrauch insgesamt WLAN Switch'),
                            ]),
                        ]),
                        html.Div(className='level-item has-text-centered', children=[
                            html.Div(children=[
                                html.Div(className='is-inline-block', children=[
                                    dcc.Graph(figure=switch_current_fig, config=dict(locale='de')),
                                ]),
                                html.P(className='heading', children='Stromstärke WLAN Switch'),
                            ]),
                        ]),
                    ]),
                ]),
                html.Div(className='tile block', children=[
                    html.Div(className='tile is-vertical is-parent', children=[
                        html.Div(className='tile is-child notification px-5', children=[
                            html.Div(className='level mb-2', children=[
                                html.Div(className='level-left', children=[
                                    html.Div(className='level-item', children=[
                                        html.H5(className='title is-5', children='Temperatur'),
                                    ]),
                                ]),
                                html.Div(className='level-right', children=[
                                    html.Div(className='level-item', children=[
                                        html.Span(className='tag is-dark', children=f'{current_temp}°C'),
                                    ]),
                                ]),
                            ]),
                            dcc.Graph(id='temp-graph', figure=temp_fig, config=dict(displayModeBar=False, locale='de')),
                        ]),
                        html.Div(className='tile is-child notification', children=[
                            html.H5(className='title is-5', children=overall_climate),
                            html.Div(className='content', children=[
                                html.Ul(className='ml-4', children=[html.Li(children=message) for message in climate_messages]),
                            ]),
                        ]),
                    ]),
                    html.Div(className='tile is-vertical is-parent', children=[
                        html.Div(className='tile is-child notification px-5', children=[
                            html.Div(className='level mb-2', children=[
                                html.Div(className='level-left', children=[
                                    html.Div(className='level-item', children=[
                                        html.H5(className='title is-5', children='Luftfeuchtigkeit'),
                                    ]),
                                ]),
                                html.Div(className='level-right', children=[
                                    html.Div(className='level-item', children=[
                                        html.Span(className=f'tag is-{hum_status}', children=f'{current_hum}%'),
                                    ]),
                                ]),
                            ]),
                            dcc.Graph(className='tile', figure=hum_fig, config=dict(displayModeBar=False, locale='de')),
                        ]),
                        html.Div(className='tile is-child notification px-5', children=[
                            html.Div(className='level mb-2', children=[
                                html.Div(className='level-left', children=[
                                    html.Div(className='level-item', children=[
                                        html.H5(className='title is-5', children=['CO', html.Sub(children='2')]),
                                    ]),
                                ]),
                                html.Div(className='level-right', children=[
                                    html.Div(className='level-item', children=[
                                        html.Span(className=f'tag is-{co2_status}', children=f'{current_co2}ppm'),
                                    ]),
                                ]),
                            ]),
                            dcc.Graph(id='co2-graph', figure=co2_fig, config=dict(displayModeBar=False, locale='de')),
                        ]),
                        html.Div(className='tile is-child notification px-5', children=[
                            html.Div(className='level mb-2', children=[
                                html.Div(className='level-left', children=[
                                    html.Div(className='level-item', children=[
                                        html.H5(className='title is-5', children='TVOC'),
                                    ]),
                                ]),
                                html.Div(className='level-right', children=[
                                    html.Div(className='level-item', children=[
                                        html.Span(className=f'tag is-{tvoc_status}', children=f'{current_tvoc}ppb'),
                                    ]),
                                ]),
                            ]),
                            dcc.Graph(id='tvoc-graph', figure=tvoc_fig, config=dict(displayModeBar=False, locale='de')),
                        ]),
                    ]),
                ]),
                
                html.Div(className='tile'),
            ]),
            html.Div(className='tile is-parent is-vertical', children=[
                html.Div(className='tile is-child box', children=[
                    html.H5(className='title is-5', children='Vergleich WiFi Signalstärken'),
                    dcc.Graph(id='wifi-graph', figure=wifi_fig, config=dict(locale='de')),
                ]),
                html.Div(className='tile is-child box', children=[
                    html.H5(className='title is-5', children='Korrelation Lichtstärken'),
                    dcc.Graph(id='lux-graph', figure=lux_fig, config=dict(locale='de')),
                ]),
            ]),
            html.Div(className='tile is-2 is-vertical is-parent', children=[
                html.Div(className='tile is-child box', children=[
                    html.H5(className='title is-5 mb-2', children='Datenmenge nach Sensor'),
                    dcc.Graph(id='counts-graph', figure=counts_fig, config=dict(displayModeBar=False, locale='de')),
                ]),
                html.Div(className='tile is-child box', children=[
                    html.H5(className='title is-5 mb-2', children='Raumnutzung'),
                    dcc.Graph(id='illuminance-graph', figure=weekdays_fig, config=dict(displayModeBar=False)),
                ]),
                html.Div(className='tile is-child box', children=[
                    html.H5(className='title is-5 mb-2', children='Top 5 Stromverbrauch'),
                    html.P(className='heading mb-2', children='Wlan Switch'),
                    html.Table(className='table is-fullwidth is-narrow', children=[
                        html.Thead(children=html.Tr(children=[
                            html.Th(children='Datum'),
                            html.Th(children='kWh'),
                        ])),
                        html.Tbody(children=
                            [html.Tr(children=[
                                html.Td(children=row.Index.strftime('%A, %d.%m.%y')),
                                html.Td(children="{:.4f}".format(row.power))
                            ]) for row in daily_power.itertuples()]
                        )
                    ]),
                ]),
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