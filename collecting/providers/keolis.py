import datetime as dt
import os

import requests


def stations(city):
    # The city parameter is necessary so that everything works
    payload = {'key': os.environ.get('KEOLIS_API_KEY'), 'cmd': 'getstation'}
    response = requests.get(
        'http://data.keolis-rennes.com/json/?version=1.0',
        params=payload
    )
    data = response.json()
    return normalize(data)


def normalize(stations):
    stations = stations['opendata']['answer']['data']['station']
    normalized = lambda station: {
        'name': station['name'],
        'address': station['name'],
        'latitude': float(station['latitude']),
        'longitude': float(station['longitude']),
        'status': 'OPEN' if station['state'] == '1' else 'CLOSED',
        'bikes': int(station['bikesavailable']),
        'stands': int(station['slotsavailable']),
        'update': dt.datetime.strptime(station['lastupdate'].split('+')[0],
                                       '%Y-%m-%dT%H:%M:%S').isoformat()
    }
    return [
        normalized(station)
        for station in stations
    ]
