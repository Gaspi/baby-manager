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
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Load data from file
jsondata = get_json_from_zip_file(extract_file)
mdf = get_minute_df_from_json(jsondata)
df = get_hour_df_from_minute_df(mdf)

# Average sleep
mean_sleep = df['sleep'].mean()


###############################################################################
#########              Building learning parameters                   #########
###############################################################################


# Predict value at t from the [history_depth] previous values : t-1, t-2, ... t-[history_depth]
history_depth = 48

# Input vectors : remove values at time t (keep only strict history : t-1, t-2, etc.)
X = pd.concat({ f'{k}_{i}': df[k].shift(i) for k in all_babykeys for i in range(1,49) }, axis=1)
X['age'] = (df['datetime'] - df['datetime'].min()) / pd.Timedelta(hours=1)
X['day']  = X['age'] % 24
X['week'] = X['age'] % (24 * 7)

# Output vector (amount of sleep at time t)
y = df['sleep']

# Exclude first [history_depth] entries : history is not fully available
X = X[history_depth:]
y = y[history_depth:]


# Shuffling dataset (optional)
shuffle = np.random.permutation(df.index)


npX = X.reindex(shuffle).to_numpy()
npy = y.reindex(shuffle).to_numpy()
def evaluate_model(f):
    return sum(np.square(f(npX) - npy))


###############################################################################
#########                         Trivial models                      #########
###############################################################################

def constant_predict(X):
    y = np.full(len(X), mean_sleep)
    return np.maximum(np.zeros(y.shape), np.minimum(np.ones(y.shape),y))

print(f"Constant model score: {evaluate_model(constant_predict)}")


def nochange_predict(X):
    y = X[:,0]
    return np.maximum(np.zeros(y.shape), np.minimum(np.ones(y.shape),y))

print(f"No change model score: {evaluate_model(nochange_predict)}")


###############################################################################
##########                         Linear Model                       #########
###############################################################################

from sklearn import linear_model
l_reg = linear_model.LinearRegression()

l_reg.fit(X.reindex(shuffle).to_numpy(), y.reindex(shuffle).to_numpy())

def l_predict(X):
    y = l_reg.predict(X)
    return np.maximum(np.zeros(y.shape), np.minimum(np.ones(y.shape),y))

print(f"Linear model score: {evaluate_model(l_predict)}")


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

lt_reg.fit(X.reindex(shuffle).to_numpy(), y.reindex(shuffle).to_numpy())

def lt_predict(X):
    y = lt_reg.predict(X)
    return np.maximum(np.zeros(y.shape), np.minimum(np.ones(y.shape),y))

print(f"Linear tree score: {evaluate_model(lt_predict)}")


print("Predictions:")

# We start our predictions after the latest available time
predict_time = df.index.max()

predict_x = df[df.index == predict_time].drop([f'{k}_0' for k in all_babykeys], axis=1).to_numpy()
for p in range(nb_predictions):
    predict_time = predict_time + pd.to_timedelta('1h')
    print(f"{pp_timeslot(predict_time)}  ->  {lt_predict(predict_x)[0]:.0%}")
    predict_x = np.roll(predict_x, 1)
    predict_x.flat[0] = 0





