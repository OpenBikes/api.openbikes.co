import datetime as dt
import requests

from app import app
from collecting import util


def stations(city):
    # The city parameter is necessary so that everything work
    payload = {
        'key': app.config['LACUB_API_KEY'],
        'SERVICE': 'WFS',
        'VERSION': '1.1.0',
        'REQUEST': 'GetFeature',
        'TYPENAME': 'CI_VCUB_P',
        'SRSNAME': 'EPSG:4326'
    }
    response = requests.get('http://data.lacub.fr/wfs', params=payload)
    stations = util.load_xml(response.content)
    return normalize(stations)


def normalize(stations):
    extract = util.extract_element
    normalized = lambda station: {
        'name': extract(station, 'bm:nom'),
        'address': extract(station, 'bm:nom'),
        'latitude': float(extract(station, 'gml:lowercorner').split(' ')[0]),
        'longitude': float(extract(station, 'gml:lowercorner').split(' ')[1]),
        'status': 'OPEN' if extract(station, 'bm:etat') == 'CONNECTEE' else 'CLOSED',
        'bikes': int(extract(station, 'bm:nbvelos')),
        'stands': int(extract(station, 'bm:nbplaces')),
        'update': dt.datetime.strptime(extract(station, 'bm:heure'), '%Y-%m-%d %H:%M:%S').isoformat()
    }
    return [
        normalized(station)
        for station in stations.find_all('gml:featuremember')
    ]
