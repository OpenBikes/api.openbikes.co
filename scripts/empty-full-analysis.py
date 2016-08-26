'''
This script creates two contingency tables to analyze the average duration
each station in a city has been empty or full.

This script has to be run from the root of this repository (next to `run.py`).

Example usage: `python scripts/empty-full-analysis.py Toulouse`
'''

import argparse
import datetime as dt

import pandas as pd

from app import services as srv
from mongo.timeseries import query


PARSER = argparse.ArgumentParser()
PARSER.add_argument('city', type=str, help='City for which to run the analysis')
PARAMS = PARSER.parse_args()

SINCE = dt.datetime(year=2015, month=10, day=1)
UNTIL = dt.datetime.now()
# Generate all the dates between SINCE and UNTIL
DAYS = [SINCE + dt.timedelta(days=d) for d in range((UNTIL - SINCE).days + 1)]

city = next(srv.get_cities(name=PARAMS.city, serialized=False))
stations = list(srv.get_stations(city_slug=city.slug, serialized=False))

empty = pd.DataFrame(index=DAYS, columns=(station.name for station in stations))
full = pd.DataFrame(index=DAYS, columns=(station.name for station in stations))

for station in stations:
    df = station.get_updates(SINCE, UNTIL)
    df['moment'] = df.index
    df['day'] = df['moment'].apply(lambda x: x.date().isoformat())
    # Extract the time between each observation
    df['duration'] = df['moment'].diff().shift(-1)
    for day, group in df.groupby('day'):
        empty[station.name][day] = group[group['bikes'] == 0]['duration'].sum()
        full[station.name][day] = group[group['spaces'] == 0]['duration'].sum()

empty.dropna(how='all').fillna(pd.Timedelta(0)).applymap(lambda x: x.seconds).to_csv('empty.csv')
full.dropna(how='all').fillna(pd.Timedelta(0)).applymap(lambda x: x.seconds).to_csv('full.csv')
