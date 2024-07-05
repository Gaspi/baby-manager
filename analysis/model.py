# -*- coding: utf-8 -*-

extract_file = r"..\data\babyplus_data_export.zip"
nb_predictions = 10

###############################################################################
##########               Loading libraries and data                  ##########
###############################################################################

from data import (
    all_babykeys,
    birth_datetime,
    get_hour_df_from_minute_df,
    get_json_from_zip_file,
    get_minute_df_from_json,
    pp_timeslot,
    )
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import tensorflow as tf

# Load data from file
jsondata = get_json_from_zip_file(extract_file)
mdf = get_minute_df_from_json(jsondata)
df = get_hour_df_from_minute_df(mdf)

# Average sleep
mean_sleep = df['sleep'].mean()


###############################################################################
#########              Building learning parameters                   #########
###############################################################################

min_time = df['datetime'].min()
def get_time_columns(time):
    if type(time) == pd.DatetimeIndex:
        time = time.to_series()
    age = (time - min_time) / pd.Timedelta(hours=1)
    return pd.DataFrame(
        data = {
            'age': age,
            'hour': time.dt.hour,
            'day_of_week': time.dt.day_of_week,
            'day_sin': np.sin(age * (2 * np.pi / 24)),
            'day_cos': np.cos(age * (2 * np.pi / 24)),
            'week_sin': np.sin(age * (2 * np.pi / (24 * 7))),
            'week_cos': np.cos(age * (2 * np.pi / (24 * 7))),
            'year_sin': np.sin(age * (2 * np.pi / (24 * 7 * 365.25))),
            'year_cos': np.cos(age * (2 * np.pi / (24 * 7 * 365.25)))
            },
        index = time)

# Predict value at t from the [history_depth] previous values : t-1, t-2, ... t-[history_depth]
history_depth = 48

def get_history_columns(time):
    return pd.DataFrame(
        data = {
            f'{k}_{i}': [ df[k].get(t-pd.to_timedelta(i,'h'), 0) for t in time ]
            for k in all_babykeys for i in range(1,history_depth+1)
            },
        index = time)

def compute_input(time):
    return pd.concat( [get_history_columns(time), get_time_columns(time) ], axis=1)

X = compute_input(df.index)


# Output vector (amount of sleep at time t)
y = df['sleep']

# Exclude first [history_depth] entries : history is not fully available
X = X[history_depth:]
y = y[history_depth:]


# Shuffling dataset (optional)
shuffle = np.random.permutation(X.index)


npX = X.reindex(shuffle).to_numpy()
npy = y.reindex(shuffle).to_numpy()

all_zeros = np.zeros(len(npy))
all_ones  = np.ones(len(npy))
def evaluate_model(f):
    predict = np.maximum(all_zeros, np.minimum(all_ones,f(npX)))
    return sum(np.square(predict - npy))


###############################################################################
#########                         Trivial models                      #########
###############################################################################

def constant_predict(X):
    return np.full(len(X), mean_sleep)

print(f"Constant model score: {evaluate_model(constant_predict)}")


def nochange_predict(X):
    return X[:,0]

print(f"No change model score: {evaluate_model(nochange_predict)}")


###############################################################################
##########                         Linear Model                       #########
###############################################################################

from sklearn import linear_model

l_reg = linear_model.LinearRegression()
l_reg.fit(npX, npy)

print(f"Linear model score: {evaluate_model(l_reg.predict)}")


###############################################################################
##########                         Linear Tree                       ##########
###############################################################################
# Requires :
#    ```sh
#    pip install linear-tree
#    ```

from sklearn.linear_model import LinearRegression
from lineartree import LinearTreeRegressor

lt_reg = LinearTreeRegressor(base_estimator=LinearRegression())
lt_reg.fit(npX, npy)

print(f"Linear tree score: {evaluate_model(lt_reg.predict)}")


print("Predictions:")

# We start our predictions after the latest available time
predict_times = [ df.index.max() + pd.to_timedelta(t, 'h') for t in range(1,nb_predictions+1) ]
predict_X = compute_input(predict_times)
prediction = lt_reg.predict(predict_X.to_numpy())

for (t, p) in zip(predict_times, prediction) :
    print(f"{pp_timeslot(t)}  ->  {max(0, min(1, p)):.0%}")

