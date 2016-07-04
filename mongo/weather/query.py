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

from datetime import datetime

import pandas as pd

from mongo.weather import db


def rename_columns(dataframe):
    '''
    The data is stored in MongoDB with shortcuts for the attributes in order
    to save memory. This function renames the columns appropriately.
    '''
    shortcuts = {
        'd': 'description',
        'p': 'pressure',
        't': 'temperature',
        'h': 'humidity',
        'w': 'wind speed',
        't': 'temperature',
        'c': 'clouds'
    }
    dataframe.rename(columns=shortcuts, inplace=True)
    return dataframe


def fetch(city, since, until):
    # Connect to the appropriate collection of the database
    collection = db[city]
    # Query the station's updates
    cursor = collection.find({
        '_id': {
            '$gte': since.isoformat(),
            '$lte': until.isoformat()
        }
    })
    # We will modify the index so as to take into account the date
    fmt = '%Y-%m-%d/%H:%M:%S'
    # Create the dataframe with the first date
    dataframe = pd.DataFrame(cursor[0]['u']).set_index('m')
    dataframe.index = dataframe.index.map(
        lambda i: datetime.strptime('/'.join((cursor[0]['_id'], i)), fmt))
    # Add the updates from every other date
    for date in cursor[1:]:
        try:
            df = pd.DataFrame(date['u']).set_index('m')
            df.index = df.index.map(
                lambda i: datetime.strptime('/'.join((date['_id'], i)), fmt))
            dataframe = pd.concat((dataframe, df))
        except:
            pass
    # Rename the columns
    dataframe = rename_columns(dataframe)
    return dataframe
