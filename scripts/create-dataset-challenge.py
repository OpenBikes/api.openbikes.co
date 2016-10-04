'''
This script generates a sample dataset containing different timestamps.
Students will have to fill the blanks with their predictive results.

This script has to be run from the root of this repository (next to `run.py`).

Example usage: `python scripts/create-dataset-challenge.py --place 'Toulouse' '00229 - IUT RANGUEIL' --place 'Toulouse' '00189 - MURET BOUTINON'  --moment 2016/09/02-00:14:01 --blank False`

Usage: create-dataset-challenge.py [OPTIONS]

Options:
  --place <TEXT TEXT>...  City and station for which to import data
  --moment DATE           Get the data since this moment
  --blank BOOLEAN         Export real data for admins or leave blanks for
                          students (default: True)
  --help                  Show this message and exit.
'''

import datetime as dt
import os
import sys

import click
import numpy as np
import pandas as pd

# Update sys.path to access app folder
sys.path.insert(0, os.getcwd())
os.chdir(os.getcwd())

from app import services as srv
from app.exceptions import CityNotFound, CityUnpredicable
from scripts import util


DATE_TYPE = util.DateParamType()

MOMENTS = [
    {'minutes': 10},
    {'minutes': 30},
    {'hours': 1},
    {'hours': 2},
    {'hours': 4},
    {'hours': 8},
    {'hours': 24},
    {'hours': 48},
    {'hours': 72},
    {'hours': 96}
]


def find_tuple_according_moment(df, datetime_obj):
    ''' This simple method will return the values related to a
        TimeSeriesIndex entry closest to a given datetime object.
    '''
    return df.iloc[np.argmin(np.abs(df.index.to_pydatetime() - datetime_obj))]


def init_station_dataframe(city, station, moment, blank):

    click.secho('city: {}'.format(city), fg='yellow', bold=True)
    click.secho('station: {}'.format(station), fg='yellow', bold=True)
    click.secho('moment: {}'.format(moment), fg='yellow')
    click.secho('blank: {}'.format(blank), fg='blue', bold=True)

    SINCE = moment
    FILTERED_DATES = [SINCE + dt.timedelta(**moment) for moment in MOMENTS]
    UNTIL = FILTERED_DATES[-1]

    util.notify('Querying {city} in database...'.format(city=city), 'cyan')
    # Make sure the city exists
    try:
        CITY = next(srv.get_cities(name=city, serialized=False))
    except CityNotFound as exc:
        util.notify(exc, 'red')
        sys.exit()

    # Make sure the city is predictable
    if not CITY.predictable:
        util.notify(CityUnpredicable, 'red')
        sys.exit()

    util.notify('Querying {city} stations in database...'.format(city=city), 'cyan')

    # Search city station
    STATION = next(srv.get_stations(name=station, city_slug=CITY.slug, serialized=False))

    # Get bike updates
    if not blank:
        util.notify('Getting station updates...', 'cyan')
        try:
            df = STATION.get_updates(SINCE, UNTIL)
        except Exception as exc:
            util.notify(exc, 'red')
            sys.exit()

    util.notify('Generating dataframe...', 'cyan')
    # Create dataframe
    columns = dict(
        bikes=[find_tuple_according_moment(df, moment).bikes for moment in FILTERED_DATES] if not blank else
        [''] * len(FILTERED_DATES),
        station=[station] * len(FILTERED_DATES),
        city=[city] * len(FILTERED_DATES)
    )

    index = FILTERED_DATES

    column_order = ['city', 'station', 'bikes']
    return pd.DataFrame(columns, index)[column_order]


@click.command()
@click.option('--place', type=(str, str), help='City and station for which to import data', multiple=True)
@click.option('--moment', type=DATE_TYPE, help='Get the data since this moment')
@click.option('--blank', type=bool, help='Export real data for admins or leave blanks for students (default: True)', default=True)
def create_dataset_challenge(place, moment, blank):

    dataframes = (init_station_dataframe(city=obj[0], station=obj[1], moment=moment, blank=blank) for obj in place)
    dataset = pd.concat(dataframes, axis=0, ignore_index=False)
    print(dataset)

    try:
        util.notify('Saving global dataframe...', 'cyan')
        dataset.to_csv('dataset.csv')
    except Exception as exc:
        print(exc)
        util.notify(exc, 'red')
        sys.exit()

    util.notify('Done!', 'green')

if __name__ == '__main__':
    create_dataset_challenge()
