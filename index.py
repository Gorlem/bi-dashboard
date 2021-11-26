import env

import dash
from dash import dcc
from dash import html
from dash.dependencies import Output, Input
from dash.exceptions import PreventUpdate

import plotly.express as px

from sqlalchemy import create_engine

import pandas as pd


app = dash.Dash(__name__)

engine = create_engine(f'mysql+pymysql://{env.USER}:{env.PASSWORD}@{env.SERVER}/{env.DATABASE}?charset=utf8mb4')

illuminance = pd.read_sql('SELECT created, CAST(state as FLOAT) as state FROM states WHERE entity_id = \'sensor.bh1750_illuminance_2\' ORDER BY created DESC LIMIT 10', engine, index_col='created')

print(illuminance.head())

illuminance_fig = px.line(illuminance)

bme280_humidity = pd.read_sql('SELECT created, CAST(state as FLOAT) as bme280 FROM states WHERE entity_id = \'sensor.bme280_humidity\' AND created >= \'2021-11-20\' ORDER BY created DESC', engine, index_col='created')
dht22_humidity = pd.read_sql('SELECT created, CAST(state as FLOAT) as dht22 FROM states WHERE entity_id = \'sensor.dht22_humidity\' AND created >= \'2021-11-20\' ORDER BY created DESC', engine, index_col='created')

humidity = bme280_humidity.append(dht22_humidity)

print(humidity.head())

humidty_fig = px.line(humidity)

wifi1 = pd.read_sql('SELECT created, AVG(CAST(state as INT)) as wifi1 FROM states WHERE entity_id = \'sensor.sensor_1_wifi_signal\' GROUP BY CAST(created as DATE) ORDER BY created DESC', engine, index_col='created')
wifi2 = pd.read_sql('SELECT created, AVG(CAST(state as INT)) as wifi2 FROM states WHERE entity_id = \'sensor.sensor_2_wifi_signal\' GROUP BY CAST(created as DATE) ORDER BY created DESC', engine, index_col='created')
wifi3 = pd.read_sql('SELECT created, AVG(CAST(state as INT)) as wifi3 FROM states WHERE entity_id = \'sensor.sensor_3_wifi_signal\' GROUP BY CAST(created as DATE) ORDER BY created DESC', engine, index_col='created')

wifi = wifi1.append(wifi2).append(wifi3)

print(wifi.head())

wifi_fig = px.line(wifi)

counts = pd.read_sql('SELECT entity_id, COUNT(*) as count FROM states GROUP BY entity_id', engine)

mapping = {
    'Sensor 1': [
        'sensor.bh1750_illuminance',
        'sensor.bme280_humidity',
        'sensor.bme280_pressure',
        'sensor.bme280_temperature',
        'sensor.sensor_1_firmware_version',
        'binary_sensor.sensor_1_sensor_status',
        'sensor.sensor_1_uptime',
        'sensor.sensor_1_wifi_signal',
    ],
    'Sensor 2': [
        'sensor.bh1750_illuminance_2',
        'sensor.sensor_2_firmware_version',
        'binary_sensor.sensor_2_sensor_status',
        'sensor.sensor_2_uptime',
        'sensor.sensor_2_wifi_signal',
    ],
    'Sensor 3': [
        'sensor.ccs811_eco2_value',
        'sensor.ccs811_total_volatile_organic_compound',
        'sensor.dht22_temperature',
        'sensor.dht22_humidity',
        'sensor.mh_z19_co2_value',
        'sensor.sensor_3_firmware_version',
        'binary_sensor.sensor_3_sensor_status',
        'sensor.sensor_3_uptime',
        'sensor.sensor_3_wifi_signal',
    ],
    'Smartplug 1': [
        'sensor.wlan_switch_energy_apparentpower',
        'sensor.wlan_switch_energy_current',
        'sensor.wlan_switch_energy_factor',
        'sensor.wlan_switch_energy_power',
        'sensor.wlan_switch_energy_reactivepower',
        'sensor.wlan_switch_energy_today',
        'sensor.wlan_switch_energy_total',
        'sensor.wlan_switch_energy_voltage',
        'sensor.wlan_switch_energy_yesterday',
    ],
    'Smartplug 3': [
        'sensor.smartplug3_energy_apparentpower',
        'sensor.smartplug3_energy_current',
        'sensor.smartplug3_energy_factor',
        'sensor.smartplug3_energy_power',
        'sensor.smartplug3_energy_reactivepower',
        'sensor.smartplug3_energy_today',
        'sensor.smartplug3_energy_total',
        'sensor.smartplug3_energy_voltage',
        'sensor.smartplug3_energy_yesterday',
    ],
}

names = {
    'sensor.bh1750_illuminance': 'Beleuchtungsstärke',
    'sensor.bme280_humidity': 'Feuchtigkeit',
    'sensor.bme280_pressure': 'Luftdruck',
    'sensor.bme280_temperature': 'Temperatur',
    'sensor.sensor_1_firmware_version': 'Firmware Version',
    'binary_sensor.sensor_1_sensor_status': 'Sensorstatus',
    'sensor.sensor_1_uptime': 'Uptime',
    'sensor.sensor_1_wifi_signal': 'WiFi-Signal',
    'sensor.bh1750_illuminance_2': 'Beleuchtungsstärke',
    'sensor.sensor_2_firmware_version': 'Firmware Version',
    'binary_sensor.sensor_2_sensor_status': 'Sensorstatus',
    'sensor.sensor_2_uptime': 'Uptime',
    'sensor.sensor_2_wifi_signal': 'WiFi-Signal',
    'sensor.ccs811_eco2_value': 'CO2 errechnet',
    'sensor.ccs811_total_volatile_organic_compound': 'TVOC',
    'sensor.dht22_temperature': 'Temperatur',
    'sensor.dht22_humidity': 'Feuchtigkeit',
    'sensor.mh_z19_co2_value': 'CO2',
    'sensor.sensor_3_firmware_version': 'Firmware Version',
    'binary_sensor.sensor_3_sensor_status': 'Sensorstatus',
    'sensor.sensor_3_uptime': 'Uptime',
    'sensor.sensor_3_wifi_signal': 'WiFi-Signal',
    'sensor.wlan_switch_energy_apparentpower': 'Scheinleistung',
    'sensor.wlan_switch_energy_current': 'Stromstärke',
    'sensor.wlan_switch_energy_factor': 'Phasenverschiebung',
    'sensor.wlan_switch_energy_power': 'Leistung',
    'sensor.wlan_switch_energy_reactivepower': 'Blindleistung',
    'sensor.wlan_switch_energy_today': 'Stromverbrauch (Tag)',
    'sensor.wlan_switch_energy_total': 'Stromverbrauch (total)',
    'sensor.wlan_switch_energy_voltage': 'Netzspannung',
    'sensor.wlan_switch_energy_yesterday': 'Stromverbrauch (Vortag)',
    'sensor.smartplug3_energy_apparentpower': 'Scheinleistung',
    'sensor.smartplug3_energy_current': 'Stromstärke',
    'sensor.smartplug3_energy_factor': 'Phasenverschiebung',
    'sensor.smartplug3_energy_power': 'Leistung',
    'sensor.smartplug3_energy_reactivepower': 'Blindleistung',
    'sensor.smartplug3_energy_today': 'Stromverbrauch (Tag)',
    'sensor.smartplug3_energy_total': 'Stromverbrauch (total)',
    'sensor.smartplug3_energy_voltage': 'Netzspannung',
    'sensor.smartplug3_energy_yesterday': 'Stromverbrauch (Vortag)',
}

total_count = counts['count'].sum()

def sensor_mapping(row):
    for key in mapping:
        if row['entity_id'] in mapping[key]:
            return key + ' ' + str(int(counts['count'].where(counts['entity_id'].isin(mapping[key])).sum() / total_count * 100)) + '%'
    
    return 'Unknown'

def name_mapping(row):
    if row['entity_id'] in names:
        return names[row['entity_id']] + ' ' + str(int(row['count'] / total_count * 100)) + '%'
    
    return row['entity_id']

counts['type'] = counts.apply(sensor_mapping, axis=1)
counts['*'] = 'total'
counts['name'] = counts.apply(name_mapping, axis=1)

counts_fig = px.sunburst(counts, path=['*', 'type', 'name'], values='count', maxdepth=2)

app.layout = html.Div(children=[
    html.H1(children='Test Site'),
    dcc.Graph(id='illuminance-graph', figure=illuminance_fig),
    dcc.Graph(id='humidity-graph', figure=humidty_fig),
    dcc.Graph(id='wifi-graph', figure=wifi_fig),
    dcc.Graph(id='counts-graph', figure=counts_fig),
    dcc.Interval(id='interval', interval=1000, n_intervals=0) # 1s
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