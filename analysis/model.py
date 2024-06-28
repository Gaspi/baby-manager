# -*- coding: utf-8 -*-
"""
Created on Sun Jun 23 10:37:04 2024

@author: PC
"""

# -*- coding: utf-8 -*-

extract_file = r"../babyplus_data_export (2).zip"
nb_predictions = 10

from data import birth_datetime, load_data, get_sleep_min_df, pp_timeslot
import pandas as pd
import numpy as np

data = load_data(extract_file)
sleep = get_sleep_min_df(data)


start_date = '2024-06-22 10:00:00'

start_date = birth_datetime.ceil('h')+pd.to_timedelta('48h')

hsleep = sleep.groupby( sleep.datetime.dt.floor('h') ).agg({'sleep':'sum'}) / 60


df = hsleep.join(hsleep.shift(range(1,48)))

dt = df.index
filt = (dt > start_date) & (dt < dt.max())



learn_dataset = df[filt].sample(frac=1)
X = learn_dataset.drop('sleep', axis=1).to_numpy()
y = learn_dataset['sleep'].to_numpy()


print("Learning...")

from sklearn.linear_model import LinearRegression
from lineartree import LinearTreeRegressor
regr  = LinearTreeRegressor(base_estimator=LinearRegression())

regr.fit(X, y)


print("Predictions:")


predict_time = dt.max()
predict_x = df[dt == predict_time].drop('sleep', axis=1).to_numpy()
for p in range(nb_predictions):
    print(f"{pp_timeslot(predict_time)}  ->  {regr.predict(predict_x)[0]}")
    predict_time = predict_time + pd.to_timedelta('1h')
    predict_x = np.roll(predict_x, 1)
    predict_x.flat[0] = 0


