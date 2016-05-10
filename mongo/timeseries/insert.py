from datetime import datetime

from mongo.timeseries import db

'''
'u': updates
'i': information
'm': update time
'b': available bikes
's': available stands
'''

def city(city, stations):
    ''' Add the latest update from every station in a city. '''
    # Connect to the appropriate collection of the database
    collection = db[city]
    # Update every station
    for station in stations:
        update_station(collection, station)


def update_station(collection, station):
    ''' Add the latest update of a station. '''
    name = station['name']
    timestamp = datetime.strptime(station['update'], '%Y-%m-%dT%H:%M:%S')
    time = timestamp.time().isoformat()
    date = timestamp.date().isoformat()
    # Check the dates has already been inserted
    if collection.find({'_id': date}).count() == 0:
        collection.save({
            '_id': date,
            'u': []
        })
    # Add the station entry if it doesn't exist and there is data
    if collection.find({'_id': date, 'u.n': name}).count() == 0:
        collection.update({'_id': date, 'u.n': {'$nin': [name]}}, {
            '$push': {
                'u': {
                    'n': name,
                    'i': []
                }
            }
        })
    # Update the station with the new information
    if collection.find({'_id': date, 'u.n': name, 'u.i.m': time}).count() == 0:
        collection.update({'_id': date, 'u.n': name}, {
            '$push': {
                'u.$.i': {
                    'm': time,
                    'b': station['bikes'],
                    's': station['stands']
                }
            }
        })
