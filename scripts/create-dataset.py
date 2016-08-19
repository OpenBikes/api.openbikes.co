'''
This script creates a directory named after a city in the same directory it is launched from. The
created directory contains:

- A sub-directory containing a CSV file for each station.
- A CSV file containing city's weather entries.
- A CSV file containing the coordinates of each station.

The datasets are made up with all the data on the local machine.

This script has to be run from the root of this repository (next to `run.py`).

Example usage: `python scripts/create-dataset.py Toulouse`
'''

import argparse
import datetime as dt
import os
import sys

import pandas as pd

from app import services as srv
from app.exceptions import CityNotFound, CityUnpredicable
from mongo.weather import query as weather
from mongo.timeseries import query as ts
from scripts import util


PARSER = argparse.ArgumentParser()
PARSER.add_argument('city', type=str, help='City for which to import data')
PARAMS = PARSER.parse_args()

# Make sure the city exists
try:
    CITY = next(srv.get_cities(name=PARAMS.city))
except CityNotFound as exc:
    util.notify(exc, 'red')

# Make sure the city is predictable
if not CITY['predictable']:
    util.notify(CityUnpredicable, 'red')

# Create the necessary folders if they don't exist
if not os.path.exists(CITY['slug']):
    os.makedirs(CITY['slug'])
if not os.path.exists(os.path.join(CITY['slug'], 'stations/')):
    os.makedirs(os.path.join(CITY['slug'], 'stations/'))

# Save the coordinates of each station
COORDINATES = pd.DataFrame(list(srv.get_stations(city_slug=CITY['slug'])))
COORDINATES.to_csv(os.path.join(CITY['slug'], 'coordinates.csv'), index=False)

# Save the data for each station
STATIONS = srv.get_stations(city_slug=CITY['slug'])

for station in STATIONS:
    df = ts.station(
        city=CITY['name'],
        station=station['name'],
        since=dt.datetime(year=1900, month=1, day=1),
        until=dt.datetime.now()
    )
    df.to_csv(os.path.join(CITY['slug'], 'stations/', '{}.csv'.format(station['slug'])))

# Save the weather data
WEATHER = weather.fetch(
    city=CITY['name'],
    since=dt.datetime(year=1900, month=1, day=1),
    until=dt.datetime.now()
)
WEATHER.to_csv(os.path.join(CITY['slug'], 'weather.csv'))
