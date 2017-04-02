import datetime as dt

from bs4 import BeautifulSoup

from app.util import slugify


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
                'properties': dict(
                    entry,
                    **{'slug': slugify(entry['name'])}
                ),
            } for entry in json_object
        ]
    }

    # Remove the duplicated latitude and longitude
    for feature in geojson['features']:
        del feature['properties']['latitude']
        del feature['properties']['longitude']
    return geojson


def epoch_to_datetime(epoch, divisor=1):
    ''' Convert a UNIX timestamp to a datetime. '''
    moment = dt.datetime.fromtimestamp(round(epoch / divisor))
    return moment


def load_xml(string):
    ''' Convenience wrapper for the BeautifulSoup library. '''
    return BeautifulSoup(string, 'html.parser')


def extract_element(element, child):
    ''' Extract the content of a child element from an XML element. '''
    value = element.find(child)
    return value.string if value else ''


def extract_attribute(element, attribute):
    ''' Extract an attribute from an XML element. '''
    value = element.get(attribute)
    return value
