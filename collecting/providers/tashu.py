import requests


def stations(city):
    # The city parameter is necessary so that everything works
    response = requests.get('http://www.tashu.or.kr/mapAction.do?process=statusMapView')
    data = response.json()
    return normalize(data)


def normalize(stations):
    stations = stations['markers']
    normalized = lambda station: {
        'name': station['name'],
        'address': station['name'],
        'latitude': float(station['lat']),
        'longitude': float(station['lng']),
        'status': 'OPEN',
        'bikes': int(station['cntLockOff']),
        'stands': int(station['cntRentable']),
    }
    return [
        normalized(station)
        for station in stations
    ]
