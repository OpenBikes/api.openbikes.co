'''
This script list city stations. It can be useful to retrieve stations IDs.
For example some station names contain an ID like '00229 - IUT RANGUEIL', this script 
has been made to find the exact ID of all city stations.

This script has to be run from the root of this repository (next to `run.py`).

Example usage: `python scripts/list_city_stations.py --city Toulouse`

Usage: list_city_stations.py [OPTIONS]

Options:
  --city TEXT  City name
  --help       Show this message and exit.
'''

import os
import sys

import click

# Update sys.path to access app folder
sys.path.insert(0, os.getcwd())
os.chdir(os.getcwd())

from app import services as srv
from app.exceptions import CityNotFound, CityUnpredicable
from scripts import util


def get_city_stations(city):

    click.secho('city: {}'.format(city), fg='yellow', bold=True)

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

    # Search city stations
    return srv.get_stations(city_slug=CITY.slug, serialized=False)


@click.command()
@click.option('--city', type=str, help='City name')
def main(city):

    stations = get_city_stations(city)
    for station in stations:
        print('station {}'.format(station))

if __name__ == '__main__':
    main()
