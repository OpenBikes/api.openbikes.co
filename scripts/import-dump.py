import subprocess
import time
import argparse
import datetime as dt

from pymongo import MongoClient
from termcolor import colored

parser = argparse.ArgumentParser()

parser.add_argument('city', type=str, help='City for which to import data.')
parameters = parser.parse_args()
city = parameters.city

# Create a SSH tunnel in the background
tunnel_command = 'ssh -f -N -L 2000:localhost:27017 46.101.234.224 -l max'
subprocess.call(tunnel_command, shell=True)

# Define the remote and the local connections
remote_conn = MongoClient(port=2000)
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

notify('Established database connections', 'green')

# Check if there already is some data in the local database
if C['local']['ts'].find().count() != 0:
	# Get the most recent date in the local database
	max_date = C['local']['ts'].find_one(sort=[('_id', -1)])['_id']
	# Delete the latest document in case of incomplete data
	C['local']['ts'].delete_one({'_id': max_date})
	notify('Will only import data for {0} after {1} (included)'.format(city, max_date), 'yellow')
	# Query the relevant data on the remove server
	cursor = C['remote']['ts'].find({'_id': {'$gte': max_date}}, sort=[('_id', 1)])
else:
	notify('Importing all data for {} (this could take a while)'.format(city), 'yellow')
	# Query the relevant data on the remove server
	cursor = C['remote']['ts'].find(sort=[('_id', 1)])

total = cursor.count()
notify('Fetched {0} document(s)'.format(total), 'cyan')
# Insert it locally
for i, c in enumerate(cursor):
	notify('Inserting document {0} out of {1}'.format(i + 1, total), 'cyan')
	C['local']['ts'].insert(c) 
notify('Done', 'green')
