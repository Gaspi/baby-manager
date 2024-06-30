# -*- coding: utf-8 -*-
import json, zipfile
import pandas as pd
import numpy as np

birth = '2024-05-03 09:58:00'
birth_datetime = pd.to_datetime(birth)

now = pd.Timestamp.now().tz_localize(None).ceil(freq='s')

all_babykeys = ['sleep', 'nursingfeed', 'bottlefeed', 'nappy']

def parse_datetime(d):
    res = pd.to_datetime(d).tz_localize(None).ceil(freq='s')
    return now if res.year == 1970 else res

def get_json_from_zip_file(file):
    with zipfile.ZipFile(file, "r") as z:
        for filename in z.namelist():  
            with z.open(filename) as f:  
                return json.loads(f.read())
            
def get_minute_df_from_json(data):
    sleep       = data['baby_sleep']
    nursingfeed = data['baby_nursingfeed']
    bottlefeed  = data['baby_bottlefeed']
    nappy       = data['baby_nappy']
    
    last_sleep       = parse_datetime(      sleep[0]['endDate'])
    last_nursingfeed = parse_datetime(nursingfeed[0]['endDate'])
    last_bottlefeed  = parse_datetime( bottlefeed[0]['date'])
    last_nappy       = parse_datetime(      nappy[0]['date'])
    
        
    last_date = max(last_sleep, last_nursingfeed, last_bottlefeed, last_nappy)
    daterange= pd.date_range(start=birth, end=last_date, freq='min')
    
    # Init dataframe with datetime index
    df = pd.DataFrame({'datetime': daterange})
    df.set_index('datetime', inplace=True, drop=False)
    df['date'] = df['datetime'].dt.date
    df['time'] = df['datetime'].dt.time
    
    # Actual data
    df['sleep']       = sum( [ (df['datetime'] >= parse_datetime(e['startDate'])) & (df['datetime'] < parse_datetime(e['endDate'])) for e in sleep ] )
    df['nursingfeed'] = sum( [ (df['datetime'] >= parse_datetime(e['startDate'])) & (df['datetime'] < parse_datetime(e['endDate'])) for e in nursingfeed ] )
    df['bottlefeed']  = sum( [ (df['datetime'] == parse_datetime(e['date'])) *  e['amountML'] for e in bottlefeed ] )
    df['nappy']       = sum( [ (df['datetime'] == parse_datetime(e['date'])) for e in nappy ] )
    return df


def get_hour_df_from_minute_df(mdf):
    df = mdf.groupby( mdf.datetime.dt.floor('h') ).agg({
        'datetime'   : 'min',
        'sleep'      : lambda group: np.sum(group) / 60,
        'nursingfeed': 'sum',
        'bottlefeed' : 'sum',
        'nappy'      : 'sum',
        })
    # Return the dataframe of all entries
    # except for the first and last available hours
    # which are most likely incomplete
    return df[1:-1]


# Pretty printing function to print 1h intervals using their bounds
def pp_timeslot(t, delta='1h'):
    return "[{} - {}]".format(t,t+pd.to_timedelta(delta))

