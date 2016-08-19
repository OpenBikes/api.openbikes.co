'''
This script imports timeseries data and weather data from the remote MongoDB database and dumps it
into the local database. This can be factorized for both datasets as they have the same top-level
structure (their indexes are datetimes).

The script will use the latest date in the local database to know how much data to import. If no
previous entries exist then all the data will be imported. Running the script will basically sync
the local database with the remote database.

This script has to be run from the root of this repository (next to `run.py`).

Example usage: `python import-mongo-dump.py Toulouse`
'''

import argparse
import time

from pymongo import MongoClient
from tqdm import tqdm

from mongo.utils import create_remote_connexion
from scripts import util


START_TIME = time.time()


def fetch(city_name, local, remote):
    util.notify('Fetching...', 'green', START_TIME)
    # Check if there already is some data in the local database
    if local.find().count() != 0:
        # Get the most recent date in the local database
        max_date = local.find_one(sort=[('_id', -1)])['_id']
        # Delete the latest document to avoid incomplete data
        local.delete_one({'_id': max_date})
        util.notify('Will only import data for {0} after {1} (included)'.format(city_name, max_date), 'yellow', START_TIME)
        # Query the relevant data on the remove server
        cursor = remote.find({'_id': {'$gte': max_date}}, sort=[('_id', 1)])
    else:
        util.notify('Importing all data for {} (this could take a while)'.format(city_name), 'yellow', START_TIME)
        # Query the relevant data on the remove server
        cursor = remote.find(sort=[('_id', 1)])

    total = cursor.count()
    util.notify('Fetched {0} document(s)'.format(total), 'cyan', START_TIME)
    # Insert it locally
    for i, cur in tqdm(enumerate(cursor)):
        local.insert(cur)
    util.notify('Done', 'green')


if __name__ == '__main__':
    PARSER = argparse.ArgumentParser()
    PARSER.add_argument('city', type=str, help='City for which to import data')
    PARAMS = PARSER.parse_args()
    CITY_NAME = PARAMS.city

    util.notify('Attempting to retrieve data for {}'.format(CITY_NAME), 'green', START_TIME)

    # Define the remote and the local connections
    REMOTE_CONN = create_remote_connexion()
    LOCAL_CONN = MongoClient()

    # Define the different collections
    C = {
        'local': {
            'ts': LOCAL_CONN.OpenBikes[CITY_NAME],
            'weather': LOCAL_CONN.OpenBikes_Weather[CITY_NAME]
        },
        'remote': {
            'ts': REMOTE_CONN.OpenBikes[CITY_NAME],
            'weather': REMOTE_CONN.OpenBikes_Weather[CITY_NAME]
        }
    }

    util.notify('Established connection to the remote database', 'green', START_TIME)

    util.notify('Begun retrieving bike station updates', 'green', START_TIME)
    fetch(CITY_NAME, C['local']['ts'], C['remote']['ts'])
    util.notify('Finished retrieving bike station updates', 'green', START_TIME)

    util.notify('Begun retrieving weather updates', 'green', START_TIME)
    fetch(CITY_NAME, C['local']['weather'], C['remote']['weather'])
    util.notify('Finished retrieving weather updates', 'green', START_TIME)
