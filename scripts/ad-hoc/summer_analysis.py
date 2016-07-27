from pymongo import MongoClient
from datetime import datetime
import pandas as pd
from bson.objectid import ObjectId
import click

from mongo.utils import mongo_conn

DESC = 1
MONGO_ID_FMT = '%Y-%m-%d'
DATE_ARG_FMT = '%d-%m-%Y'
LOCAL_MONGO_PORT = 27017


def filter_by_window_boundaries(since=None, until=None):
    if since:
        date_constraint = {'$gte': since}
    if until:
        date_constraint = {'$lte': until}
    if since and until:
        date_constraint = {'$gte': since, '$lte': until}
    return date_constraint


def last_record_time(collection, way=DESC):
    return datetime.strptime(list(collection.find({}, {'_id': 1})
                                  .sort('_id', way)
                                  .limit(1))[0].get('_id'), MONGO_ID_FMT).strftime(MONGO_ID_FMT)


def rename_columns(dataframe):
    '''
    The data is stored in MongoDB with shortcuts for the attributes in order
    to save memory. This function renames the columns appropriately.
    '''
    shortcuts = {
        'b': 'bikes',
        's': 'spaces'
    }
    dataframe.rename(columns=shortcuts, inplace=True)
    return dataframe


def get_city_data(db, city, since=None, until=None):
    '''
    Returns a dictionary of dataframes containing all the data for a city.
    '''

    # Connect to the appropriate collection of the database
    collection = db[city]

    start = datetime.strptime(since, DATE_ARG_FMT).strftime(MONGO_ID_FMT) if since else last_record_time(collection)
    end = datetime.strptime(
        until, DATE_ARG_FMT).strftime(MONGO_ID_FMT) if until else datetime.now().strftime(MONGO_ID_FMT)

    query_filter = filter_by_window_boundaries(start, end)

    # Query the city's collection
    cursor = collection.find({'_id': query_filter})

    # We will modify the index so as to take into account the date
    fmt = '%Y-%m-%d/%H:%M:%S'
    # Create a dictionary that will contain the dataframes
    dates_dfs = {}
    # Iterate over every date
    for date in cursor:
        # Convert all the updates to a dictionary of dataframes indexed on time
        dates_dfs[date['_id']] = {
            update['n']: pd.DataFrame(update['i']).set_index('m')
            for update in date['u']
            if len(update['i']) > 0
        }
    # Now we can merge the dataframes for every station
    stations_dfs = {}
    for date, stations in dates_dfs.items():
        for station, df in stations.items():
            # Add the date to the time for a unique index
            df.index = df.index.map(
                lambda i: datetime.strptime('/'.join((date, i)), fmt))
            # Concatenate the daily dataframes into one for the month
            if station in stations_dfs.keys():
                stations_dfs[station] = pd.concat((stations_dfs[station], df))
            else:
                stations_dfs[station] = df

    # Rename the columns
    stations_dfs = {station: rename_columns(station_df) for station, station_df in stations_dfs.items()}
    return stations_dfs


@click.command()
@click.option('--city', '-c', help='City collection to query', type=str)
@click.option('--since', '-s', help="Filter data since (optional) - format 'dd-mm-yyyy'", default=None, type=str)
@click.option('--until', '-u', help="Filter data until (optional) - format 'dd-mm-yyyy'", default=None, type=str)
@click.option('--export', '-e', help="Save dataframe to .csv ?", default=False, type=bool)
def main(city, since, until, export):
    db = mongo_conn().OpenBikes
    data = get_city_data(db, city, since, until)
    temp_dfs = []
    for station, dataframe in data.items():
        dataframe['station'] = station
        temp_dfs.append(dataframe)
    df2d = pd.concat(temp_dfs, axis=0)
    print(df2d)
    if export:
        df2d.to_csv('{}_{}_{}.csv'.format(city, since, until))


if __name__ == '__main__':
    main()
