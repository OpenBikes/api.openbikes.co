'''
This scripts imports timeseries data and weather data from the remote database
and dumps it into the local database. This can be factorized for both datasets
as they have the same top-level structure (their indexes are datetimes).

The script will use the latest date in the local database to know how much data
to import. If no previous entries exist then all the data will be imported.
Running the script will basically sync the local database with the remote
database.

This script can be run from any directory.

Example usage: `python scripts/import-dump.py Toulouse`
'''

import argparse
import datetime as dt
import subprocess
import time

from pymongo import MongoClient
from termcolor import colored

from mongo.utils import mongo_conn


parser = argparse.ArgumentParser()
parser.add_argument('city', type=str, help='City for which to import data')
parameters = parser.parse_args()
city = parameters.city

# Define the remote and the local connections
remote_conn = mongo_conn()
local_conn = MongoClient()

# Measure elapsed time along the import process
start = time.time()
now = lambda: dt.timedelta(seconds=time.time() - start)
notify = lambda m, c: print(colored('{0} - {1}'.format(now(), m), c))

# Define the different collections
C = {
    'local': {
        'ts': local_conn.OpenBikes[city],
        'weather': local_conn.OpenBikes_Weather[city]
    },
    'remote': {
        'ts': remote_conn.OpenBikes[city],
        'weather': remote_conn.OpenBikes_Weather[city]
    }
}


def fetch(local, remote):
    notify('Fetching...', 'green')
    # Check if there already is some data in the local database
    if local.find().count() != 0:
        # Get the most recent date in the local database
        max_date = local.find_one(sort=[('_id', -1)])['_id']
        # Delete the latest document to avoid incomplete data
        local.delete_one({'_id': max_date})
        notify('Will only import data for {0} after {1} (included)'.format(city, max_date), 'yellow')
        # Query the relevant data on the remove server
        cursor = remote.find({'_id': {'$gte': max_date}}, sort=[('_id', 1)])
    else:
        notify('Importing all data for {} (this could take a while)'.format(city), 'yellow')
        # Query the relevant data on the remove server
        cursor = remote.find(sort=[('_id', 1)])

    total = cursor.count()
    notify('Fetched {0} document(s)'.format(total), 'cyan')
    # Insert it locally
    for i, c in enumerate(cursor):
        notify('Inserting document {0} out of {1}'.format(i + 1, total), 'cyan')
        local.insert(c)
    notify('Done', 'green')


notify('BIKE STATIONS', 'green')
fetch(C['local']['ts'], C['remote']['ts'])

notify('WEATHER', 'green')
fetch(C['local']['weather'], C['remote']['weather'])
