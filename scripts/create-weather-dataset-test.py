'''
This script generates a testing dataset containing weather data for many cities.

This script has to be run from the root of this repository (next to `run.py`).

Example usage:`python scripts/create-weather-dataset-test.py --city toulouse --city paris --city lyon --since 2016/10/05-00:06:01 --until 2016/10/09-23:59:00`

Usage: create-weather-dataset-test.py [OPTIONS]

Options:
  --city TEXT   City name
  --since DATE  Get the data since this moment
  --until DATE  Get the data until this moment
  --help        Show this message and exit.
'''
import os
import sys

import click
import numpy as np
import pandas as pd
import datetime as dt

# Update sys.path to access app folder
sys.path.insert(0, os.getcwd())
os.chdir(os.getcwd())

from app import services as srv
from app.exceptions import CityNotFound
from scripts import util

DATE_TYPE = util.DateParamType()


def retrieve_city_weather(city, since, until):
    # Make sure the city exists
    try:
        util.notify('Querying {city} in database...'.format(city=city), 'cyan')
        CITY = next(srv.get_cities(slug=city, serialized=False))
    except CityNotFound as exc:
        util.notify(exc, 'red')
        sys.exit()

    df = CITY.get_weather_updates(since, until)
    df['city'] = [CITY.slug] * len(df.index)
    return df


@click.command()
@click.option('--city', type=str, help='City name', multiple=True)
@click.option('--since', type=DATE_TYPE, help='Get the data since this moment')
@click.option('--until', type=DATE_TYPE, help='Get the data until this moment')
def create_weather_dataset(city, since, until):

    dataframes = (retrieve_city_weather(city=obj, since=since, until=until) for obj in city)
    dataset = pd.concat(dataframes, axis=0, ignore_index=False)

    util.notify('Saving global dataframe...', 'cyan')
    dataset.to_csv('test_weather.csv')

if __name__ == '__main__':
    create_weather_dataset()
