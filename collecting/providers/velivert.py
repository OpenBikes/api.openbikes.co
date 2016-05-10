import requests

from collecting import util


def stations(city):
    # The city parameter is necessary so that everything works
    response = requests.get('http://www.velivert.fr/vcstations.xml')
    data = util.load_xml(response.content)
    return normalize(data)


def normalize(stations):
    normalized = lambda station: {
        'name': station['na'],
        'address': station['na'],
        'latitude': float(station['la']),
        'longitude': float(station['lg']),
        'status': 'OPEN',
        'bikes': int(station['av']),
        'stands': int(station['fr'])
    }
    return [
        normalized(dict(station.attrs))
        for station in stations.find_all('si')
    ]
