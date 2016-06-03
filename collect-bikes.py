import os
import json

from joblib import Parallel, delayed

from app import app
from app import logger
from app import models
from collecting import collect
from mongo.timeseries import insert as insert_bikes


def json_to_geojson(json_object):
    ''' Convert to a format readable by Leaflet. '''
    geojson = {
        'type': 'FeatureCollection',
        'features': [
            {
                'type': 'Feature',
                'geometry': {
                    'type': 'Point',
                    'coordinates': [entry['longitude'], entry['latitude']]
                },
                'properties': entry,
            } for entry in json_object
        ]
    }
    # Remove the duplicated latitude and longitude
    for feature in geojson['features']:
        del feature['properties']['latitude']
        del feature['properties']['longitude']
    return geojson


def fetch_data(city):
    ''' Fetch the bikes data for a city. '''
    # Get the current data for a city
    try:
        stations = collect(city.provider, city.name_api)
    except:
        logger.warning("Couldn't retrieve station data", city=city.name)
        return
    # Update the database if the city can be predicted
    if city.predictable is True:
        insert_bikes.city(city.name, stations)
    # Save the data for the map
    geojson = json_to_geojson(stations)
    file_name = '{}.geojson'.format(city.name)
    path = os.path.join(app.config['GEOJSON_FOLDER'], file_name)
    with open(path, 'w') as outfile:
        json.dump(geojson, outfile)


query = models.City.query.filter_by(active=True)
cities = query.all()

Parallel(n_jobs=2)(delayed(fetch_data)(city) for city in cities)
