from mongo.weather import db

'''
'u': update
'm': time
'd': description
'p': pressure
't': temperature
'h': humidity
'w': wind speed
't': temperature
'c': clouds
'''

def city(city, weather):
    ''' Add the latest weather update for a city. '''
    # Connect to the appropriate collection of the database
    collection = db[city]
    # Extract the date
    date = weather['datetime'].date().isoformat()
    time = weather['datetime'].time().isoformat()
    # Check the dates has already been inserted
    if collection.find({'_id': date}).count() == 0:
        collection.save({
            '_id': date,
            'u': []
        })
    # Add the weather entry if it doesn't exist
    if collection.find({'_id': date, 'u.m': time}).count() == 0:
        # Update the day with the new information
        collection.update({'_id': date}, {
            '$push': {
                'u': {
                    'm': time,
                    'd': weather['description'],
                    'p': weather['pressure'],
                    't': weather['temperature'],
                    'h': weather['humidity'],
                    'w': weather['wind_speed'],
                    'c': weather['clouds']
                }
            }
        })
