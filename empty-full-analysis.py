'''
This script creates two contingency tables to analyze the average duration
each station in a city has been empty or full.

This script has to be run from the root of this repository (next to `run.py`).

Example usage: `python scripts/empty-full-analysis.py Toulouse`
'''

import argparse
import datetime as dt

import pandas as pd

from mongo.timeseries import query as ts


parser = argparse.ArgumentParser()
parser.add_argument('city', type=str, help='City for which to run the analysis')
parameters = parser.parse_args()

SINCE = dt.datetime(year=1900, month=1, day=1)
UNTIL = dt.datetime.now()
PERIOD = 'D'
PERIOD_DURATION = pd.to_timedelta(dt.timedelta(days=1))


stations = ts.city(parameters.city)



# def count_down_time(df, col):
#     df['date'] = df.index
#     df['duration'] = df['date'].shift(-1) - df['date']
#     df['duration'] = pd.to_timedelta(df['duration'])
#     # Count down time per day
#     down_time = df[df[col] == 0]['duration'].resample(PERIOD, how='sum').fillna(0)
#     down_time = down_time.apply(lambda x: min(x / PERIOD_DURATION, 1))
#     return down_time

# empty = {
#     key: count_down_time(value, 'bikes')
#     for key, value in stations.items()
# }
# df = pd.DataFrame(columns=empty.keys())
# for key, value in empty.items():
#     df[key] = value
# df.to_csv('empty.csv')

# full = {
#     key: count_down_time(value, 'spaces')
#     for key, value in stations.items()
# }
# df = pd.DataFrame(columns=full.keys())
# for key, value in full.items():
#     df[key] = value
# df.to_csv('full.csv')
