from pandas.core import groupby
import env

import pandas as pd
from sqlalchemy import create_engine, func, cast, select, distinct, Float, Table, Column, DateTime, Date, String, MetaData

metadata = MetaData()

engine = create_engine(env.CONNECTION_STRING)

states = Table('states', metadata,
    Column('created', DateTime, primary_key=True),
    Column('state', String),
    Column('entity_id', String)
)

def lux_inside():
    query = select(states.c.created, cast(states.c.state, Float).label('lux_inside'))\
        .where(states.c.entity_id == 'sensor.bh1750_illuminance')\
        .order_by(states.c.created.desc())
    
    return pd.read_sql(query, engine, index_col='created')

def lux_outside():
    query = select(states.c.created, cast(states.c.state, Float).label('lux_outside'))\
        .where(states.c.entity_id == 'sensor.bh1750_illuminance_2')
    
    return pd.read_sql(query, engine, index_col='created')

def all_switch_power():
    query = select(states.c.created, cast(states.c.state, Float).label('power'))\
        .where(states.c.entity_id == 'sensor.wlan_switch_energy_power')
    
    return pd.read_sql(query, engine, index_col='created')

def humidity_comparison():
    query_bme280 = select(states.c.created, cast(states.c.state, Float).label('bme280'))\
        .where(states.c.entity_id == 'sensor.bme280_humidity', states.c.created >= '2021-11-20')\
        .order_by(states.c.created.desc())
    
    query_dht22 = select(states.c.created, cast(states.c.state, Float).label('dht22'))\
        .where(states.c.entity_id == 'sensor.dht22_humidity', states.c.created >= '2021-11-20')\
        .order_by(states.c.created.desc())


    bme280_humidity = pd.read_sql(query_bme280, engine, index_col='created')
    dht22_humidity = pd.read_sql(query_dht22, engine, index_col='created')

    return bme280_humidity.append(dht22_humidity)

def wifi():
    query1 = select(states.c.created, func.avg(cast(states.c.state, Float)).label('Sensor #1'))\
        .where(states.c.entity_id == 'sensor.sensor_1_wifi_signal')\
        .group_by(cast(states.c.created, Date))\
        .order_by(states.c.created.desc())
    query2 = select(states.c.created, func.avg(cast(states.c.state, Float)).label('Sensor #2'))\
        .where(states.c.entity_id == 'sensor.sensor_2_wifi_signal')\
        .group_by(cast(states.c.created, Date))\
        .order_by(states.c.created.desc())
    query3 = select(states.c.created, func.avg(cast(states.c.state, Float)).label('Sensor #3'))\
        .where(states.c.entity_id == 'sensor.sensor_3_wifi_signal')\
        .group_by(cast(states.c.created, Date))\
        .order_by(states.c.created.desc())

    wifi1 = pd.read_sql(query1, engine, index_col='created')
    wifi2 = pd.read_sql(query2, engine, index_col='created')
    wifi3 = pd.read_sql(query3, engine, index_col='created')

    return wifi1.append(wifi2).append(wifi3)

def amounts():
    query = select(states.c.entity_id, func.count().label('amount'))\
        .group_by(states.c.entity_id)
    
    return pd.read_sql(query, engine)

def temperature():
    query = select(states.c.created, cast(states.c.state, Float).label('state'))\
        .where(states.c.entity_id == 'sensor.dht22_temperature', states.c.created >= func.subdate(func.now(), 7))\
        .order_by(states.c.created.desc())
    
    return pd.read_sql(query, engine, index_col='created')

def humidity():
    query = select(states.c.created, cast(states.c.state, Float).label('state'))\
        .where(states.c.entity_id == 'sensor.bme280_humidity', states.c.created >= func.subdate(func.now(), 7))\
        .order_by(states.c.created.desc())
    
    return pd.read_sql(query, engine, index_col='created')

def co2():
    query = select(states.c.created, cast(states.c.state, Float).label('state'))\
        .where(states.c.entity_id == 'sensor.mh_z19_co2_value', states.c.created >= func.subdate(func.now(), 7))\
        .order_by(states.c.created.desc())
    
    return pd.read_sql(query, engine, index_col='created')

def tvoc():
    query = select(states.c.created, cast(states.c.state, Float).label('state'))\
        .where(states.c.entity_id == 'sensor.ccs811_total_volatile_organic_compound', states.c.created >= func.subdate(func.now(), 7))\
        .order_by(states.c.created.desc())
    
    return pd.read_sql(query, engine, index_col='created')

def switch_power():
    query = select(cast(states.c.state, Float).label('state'))\
        .where(states.c.entity_id == 'sensor.wlan_switch_energy_power', states.c.created >= func.subdate(func.now(), 7))\
        .order_by(states.c.created.desc())\
    
    return pd.read_sql(query, engine)

def switch_current():
    query = select(cast(states.c.state, Float).label('state'))\
        .where(states.c.entity_id == 'sensor.wlan_switch_energy_current', states.c.created >= func.subdate(func.now(), 7))\
        .order_by(states.c.created.desc())\
    
    return pd.read_sql(query, engine)

def date_range():
    query = select(func.max(states.c.created).label('last_date'), func.min(states.c.created).label('first_date'))

    return pd.read_sql(query, engine)

def amount_of_weekdays():
    query = select(func.weekday(states.c.created).label('weekday'), func.count(distinct(cast(states.c.created, Date))).label('count'))\
        .group_by(func.weekday(states.c.created))
    
    return pd.read_sql(query, engine, index_col='weekday')

def daily_wlan_switch_power():
    query = select(states.c.created, func.max(cast(states.c.state, Float)).label('power'))\
        .where(states.c.entity_id == 'sensor.wlan_switch_energy_today')\
        .group_by(cast(states.c.created, Date))\
        .order_by(func.max(cast(states.c.state, Float)).desc())\
        .limit(5)
    
    return pd.read_sql(query, engine, index_col='created')

def total_switch_energy():
    query = select(func.max(cast(states.c.state, Float)).label('total'))\
        .where(states.c.entity_id == 'sensor.wlan_switch_energy_total')
    
    return pd.read_sql(query, engine)