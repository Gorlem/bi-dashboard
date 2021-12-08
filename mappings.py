import pandas as pd

mappings = pd.read_csv('./mappings.csv', index_col='entity_id', sep='\t')

def mapping(df):
    total_amount = df['amount'].sum()

    df['name'] = df.apply(lambda row: name_mapping(row, total_amount), axis=1)
    df['type'] = df.apply(lambda row: sensor_mapping(row, df, total_amount), axis=1)
    df['*'] = 'Total'

def sensor_mapping(row, df, total_amount):
    if row['entity_id'] in mappings.index:
        sensor = mappings.loc[row['entity_id']]['sensor']
        percentage = 0
        same_sensor = mappings[mappings.sensor == sensor].index
        sensor_total = df['amount'].where(df['entity_id'].isin(same_sensor))
        percentage = int(sensor_total.sum() / total_amount * 100)
        return f"{sensor} ({percentage}%)"
    
    return 'Unknown'

def name_mapping(row, total_amount):
    if row['entity_id'] in mappings.index:
        description = mappings.loc[row['entity_id']]['description']
        percentage = int(row['amount'] / total_amount * 100)
        return f"{description} ({percentage}%)"
    
    return row['entity_id']