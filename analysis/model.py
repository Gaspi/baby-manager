# -*- coding: utf-8 -*-

extract_file = r"..\data\babyplus_data_export.zip"
nb_predictions = 10

###############################################################################
##########               Loading libraries and data                  ##########
###############################################################################

from data import (
    add_shifted_to_hour_df,
    all_babykeys,
    get_hour_df_from_minute_df,
    get_json_from_zip_file,
    get_minute_df_from_json,
    pp_timeslot,
    )
import pandas as pd
import numpy as np

jsondata = get_json_from_zip_file(extract_file)
mdf = get_minute_df_from_json(jsondata)
hdf = get_hour_df_from_minute_df(mdf)


###############################################################################
##########                         Linear Tree                       ##########
###############################################################################
# Requires :
#    ```sh
#    pip install linear-tree
#    ```

# Predict value at t from the [history_depth] previous values : t-1, t-2, ... t-[history_depth]
history_depth = 48

# Generate extra columns for history
df = add_shifted_to_hour_df(hdf, history_depth)

# Exclude first [history_depth] entries : history is not fully available
df = df[history_depth:]


# Shuffling dataset (optional)
learn_dataset = df.sample(frac=1)

# Input vectors : remove values at time t (keep only strict history : t-1, t-2, etc.)
X = learn_dataset.drop([f'{k}_0' for k in all_babykeys], axis=1).to_numpy()

# Output vector (amount of sleep at time t)
y = learn_dataset['sleep_0'].to_numpy()


print("Learning...")

from sklearn.linear_model import LinearRegression
from lineartree import LinearTreeRegressor
regr  = LinearTreeRegressor(base_estimator=LinearRegression())

regr.fit(X, y)


print("Predictions:")

# We start our predictions after the latest available time
predict_time = hdf.index.max()

predict_x = df[df.index == predict_time].drop([f'{k}_0' for k in all_babykeys], axis=1).to_numpy()
for p in range(nb_predictions):
    predict_time = predict_time + pd.to_timedelta('1h')
    print(f"{pp_timeslot(predict_time)}  ->  {regr.predict(predict_x)[0]}")
    predict_x = np.roll(predict_x, 1)
    predict_x.flat[0] = 0

