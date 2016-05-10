import requests


def stations(city):
    # The city parameter is necessary so that everything works
    response = requests.get('http://www.bikechattanooga.com/stations/json')
    data = response.json()
    return normalize(data)


def normalize(stations):
    stations = stations['stationBeanList']
    normalized = lambda station: {
        'name': station['stationName'],
        'address': station['stAddress1'],
        'latitude': station['latitude'],
        'longitude': station['longitude'],
        'status': 'OPEN' if station['statusValue'] == 'In Service' else 'CLOSED',
        'bikes': int(station['availableBikes']),
        'stands': int(station['availableDocks'])
    }
    return [
        normalized(station)
        for station in stations
    ]
