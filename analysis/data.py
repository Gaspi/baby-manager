# -*- coding: utf-8 -*-


import json, zipfile
import pandas as pd

def load_data(file):
    with zipfile.ZipFile(file, "r") as z:
        for filename in z.namelist():  
            with z.open(filename) as f:  
                return json.loads(f.read())
            

birth = '2024-05-03 09:58:00'
birth_datetime = pd.to_datetime(birth)

now = pd.Timestamp.now().tz_localize(None).ceil(freq='s')

def parse_datetime(d):
    res = pd.to_datetime(d).tz_localize(None).ceil(freq='s')
    return now if res.year == 1970 else res

def get_sleep_min_df(data):
    sleep = data['baby_sleep']
    last_date = parse_datetime(sleep[0]['endDate'])
    datetimes = pd.date_range(start=birth, end=last_date, freq='min')
    df = pd.DataFrame({'datetime': datetimes})
    df.set_index('datetime', inplace=True, drop=False)
    df['sleep'] = sum( [ (df['datetime'] >= parse_datetime(s['startDate'])) & (df['datetime'] < parse_datetime(s['endDate'])) for s in sleep ] )
    df['date'] = df['datetime'].dt.date
    df['time'] = df['datetime'].dt.time
    return df


def pp_timeslot(t, delta='1h'):
    return "[{} - {}]".format(t,t+pd.to_timedelta(delta))

