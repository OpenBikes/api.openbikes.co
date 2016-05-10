import datetime as dt
import re

import requests


def stations(city):
    # The city parameter is necessary so that everything works
    response = requests.get('https://www.vel-in.fr/cartoV2/libProxyCarto.asp')
    data = response.json()
    return normalize(data)


def clean(s):
    if s is not None:
        s = s.lower()
        s = s.replace("+", " ")
        s = s.replace("%c3%a0", "à")
        s = s.replace("%c3%b4", "ô")
        s = s.replace("%c2%b0", "°")
        s = s.replace("%c3%a9", "é")
        s = s.replace("%c3%a7", "ç")
        s = s.replace("%27", "'")
        s = s.replace("%3a", "-")
        s = s.replace("%e2%80%99", "è")
        s = s.replace("%c3%a8", "'")
        s = s.replace("%c3%ae", "î")
        s = s.upper()
        return s


def normalize(stations):
    metadata = stations
    stations = stations['stand']
    normalized = lambda station: {
        'name': clean(str(station['name'])),
        'address': clean(station['name']),
        'latitude': float(station['lat']),
        'longitude': float(station['lng']),
        'status': 'OPEN' if station['disp'] == '1' else 'CLOSED',
        'bikes': int(station['ab']),
        'stands': int(station['ap']),
        'update': dt.datetime.strptime(metadata['gmt'], '%m/%d/%Y %H:%M:%S %p').isoformat()
    }
    return [
        normalized(station)
        for station in stations
    ]
