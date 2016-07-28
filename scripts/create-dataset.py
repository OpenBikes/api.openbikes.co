'''
This script creates a directory named after a city in the same directory where
this script is launched from. The created directory contains:

- A directory containing a .csv file for each station.
- A .csv file containing city's weather entries.
- A .csv file containing the coordinates of each station.

The datasets are made up with all the data on the local machine.

This script has to be run from the root of this repository (next to `run.py`).

Example usage: `python create-dataset.py Toulouse`
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


parser = argparse.ArgumentParser()
parser.add_argument('city', type=str, help='City for which to import data')
parameters = parser.parse_args()

# Make sure the city exists
try:
    city = next(srv.get_cities(name=parameters.city))
except CityNotFound as exc:
    print(exc)
    sys.exit()

# Make sure the city is predictable
if city['predictable'] is False:
    raise CityUnpredicable
    sys.exit()

# Create the necessary folders if they don't exist
if not os.path.exists(city['slug']):
    os.makedirs(city['slug'])
if not os.path.exists(os.path.join(city['slug'], 'stations/')):
    os.makedirs(os.path.join(city['slug'], 'stations/'))

# Save the coordinates of each station
coordinates = pd.DataFrame(list(srv.get_stations(city=city['name'])))
coordinates.to_csv(os.path.join(city['slug'], 'coordinates.csv'), index=False)

# Save the data for each station
stations = srv.get_stations(city=city['name'])

for station in stations:
    df = ts.station(city['name'],
                    station['name'],
                    since=dt.datetime(year=1900, month=1, day=1),
                    until=dt.datetime.now())
    df.to_csv(os.path.join(city['slug'], 'stations/', '{}.csv'.format(station['slug'])))

# Save the weather data
df = weather.fetch(city['name'],
                   since=dt.datetime(year=1900, month=1, day=1),
                   until=dt.datetime.now())
df.to_csv(os.path.join(city['slug'], 'weather.csv'))
