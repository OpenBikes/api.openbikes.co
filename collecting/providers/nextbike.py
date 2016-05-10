import requests

from collecting import util


def stations(city):
    payload = {'city': city}
    response = requests.get(
        'https://nextbike.net/maps/nextbike-official.xml',
        params=payload
    )
    data = util.load_xml(response.content)
    return normalize(data)


def normalize(stations):
    normalized = lambda station: {
        'name': station['name'],
        'address': station['name'],
        'latitude': float(station['lat']),
        'longitude': float(station['lng']),
        'status': 'OPEN' if station['bike_racks'] != 0 and station['bikes'] != 0 else 'CLOSED',
        'bikes': int(station['bike_racks']),
        'stands': int(station['free_racks'])
    }
    return [
        normalized(dict(station.attrs))
        for station in stations.find_all('place')
        if station.get('bike_racks') and station.get('free_racks')
    ]
