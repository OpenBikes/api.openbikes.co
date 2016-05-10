import requests

from collecting import util


def stations(city):
    # The city parameter is necessary so that everything works
    response = requests.get('http://www.decobike.com/playmoves.xml')
    data = util.load_xml(response.content)
    return normalize(data)


def normalize(stations):
    extract = util.extract_element
    normalized = lambda station: {
        'name': extract(station, 'id') + " - " + extract(station, 'address'),
        'address': extract(station, 'address'),
        'latitude': float(extract(station, 'latitude')),
        'longitude': float(extract(station, 'longitude')),
        'status': 'OPEN' if extract(station, 'address').lower() != 'not in service' else 'CLOSED',
        'bikes': int(extract(station, 'bikes')),
        'stands': int(extract(station, 'dockings'))
    }
    return [
        normalized(station)
        for station
        in stations.find_all('location')
    ]
