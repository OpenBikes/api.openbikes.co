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


# parser = argparse.ArgumentParser()
# parser.add_argument('city', type=str, help='City for which to import data')
# parameters = parser.parse_args()

# stations_dfs = ts.city(parameters.city)

df = ts.station('Toulouse',
                '00003 - POMME',
                since=dt.datetime(year=1900, month=1, day=1),
                until=dt.datetime.now())

df['date'] = df.index
df['duration'] = df['date'].shift(-1) - df['date']
df['duration'] = pd.to_timedelta(df['duration'])

empty = df[df['bikes'] == 0]
full = df[df['spaces'] == 0]

print(empty['duration'].resample('M', how='sum'))
print(full['duration'].resample('M', how='sum'))
