from pandas.core import groupby
import env

import pandas as pd
from sqlalchemy import create_engine, func, cast, select, Float, Table, Column, DateTime, Date, String, MetaData

metadata = MetaData()

engine = create_engine(env.CONNECTION_STRING)

states = Table('states', metadata,
    Column('created', DateTime, primary_key=True),
    Column('state', String),
    Column('entity_id', String)
)

def illuminance():
    query = select(states.c.created, cast(states.c.state, Float).label('lux'))\
        .where(states.c.entity_id == 'sensor.bh1750_illuminance')
    
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
    query1 = select(states.c.created, func.avg(cast(states.c.state, Float)).label('wifi1'))\
        .where(states.c.entity_id == 'sensor.sensor_1_wifi_signal')\
        .group_by(cast(states.c.created, Date))\
        .order_by(states.c.created.desc())
    query2 = select(states.c.created, func.avg(cast(states.c.state, Float)).label('wifi2'))\
        .where(states.c.entity_id == 'sensor.sensor_2_wifi_signal')\
        .group_by(cast(states.c.created, Date))\
        .order_by(states.c.created.desc())
    query3 = select(states.c.created, func.avg(cast(states.c.state, Float)).label('wifi3'))\
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
    query = select(states.c.created, states.c.state)\
        .where(states.c.entity_id == 'sensor.dht22_temperature')\
        .order_by(states.c.created.desc())\
        .limit(50)
    
    return pd.read_sql(query, engine, index_col='created')

def humidity():
    query = select(states.c.created, states.c.state)\
        .where(states.c.entity_id == 'sensor.bme280_humidity')\
        .order_by(states.c.created.desc())\
        .limit(50)
    
    return pd.read_sql(query, engine, index_col='created')

def co2():
    query = select(states.c.created, states.c.state)\
        .where(states.c.entity_id == 'sensor.mh_z19_co2_value')\
        .order_by(states.c.created.desc())\
        .limit(50)
    
    return pd.read_sql(query, engine, index_col='created')

def tvoc():
    query = select(states.c.created, states.c.state)\
        .where(states.c.entity_id == 'sensor.ccs811_total_volatile_organic_compound')\
        .order_by(states.c.created.desc())\
        .limit(50)
    
    return pd.read_sql(query, engine, index_col='created')