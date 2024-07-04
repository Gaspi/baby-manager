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
predict_time = df.index.max()

predict_x = X[X.index == X.index.max()].to_numpy()
for p in range(nb_predictions):
    predict_time = predict_time + pd.to_timedelta('1h')
    print(f"{pp_timeslot(predict_time)}  ->  {lt_predict(predict_x)[0]:.0%}")
    predict_x = np.roll(predict_x, 1)
    predict_x.flat[0] = 0





