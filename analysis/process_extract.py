# -*- coding: utf-8 -*-

extract_file = r"../babyplus_data_export (2).zip"

from data import load_data, get_sleep_min_df
import pandas as pd

data = load_data(extract_file)
df = get_sleep_min_df(data)

df['sleep24'] = df['sleep'].rolling( pd.Timedelta(1, "d") ).mean()


import matplotlib as mpl
mpl.rcParams['figure.dpi'] = 600


mpl.pyplot.figure()
ndf = df.groupby('time').agg({'sleep':['sum','count']}).droplevel(axis=1, level=0).reset_index().set_index('time')
(ndf['sum'] / ndf['count']).plot(
    legend=True,
    figsize=(15,10),
    ylim=(0,1),
    xlabel='Time of day',
    ylabel='Sleep',
    title='Dodo Sacha'
    )


mpl.pyplot.figure()
df.set_index('time').groupby('date')['sleep24'].plot(
    legend=True,
    figsize=(15,10),
    ylim=(0,1),
    xlabel='Time of day',
    ylabel='Sleep',
    title='Dodo Sacha'
    )


