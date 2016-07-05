import requests

from app import app
from collecting import util


def stations(city):
    payload = {'contract': city, 'apiKey': app.config['JCDECAUX_API_KEY']}
    response = requests.get(
        'https://api.jcdecaux.com/vls/v1/stations',
        params=payload
    )
    data = response.json()
    return normalize(data)


def normalize(stations):
    normalized = lambda station: {
        'name': station['name'],
        'address': station['address'],
        'latitude': station['position']['lat'],
        'longitude': station['position']['lng'],
        'status': station['status'],
        'bikes': station['available_bikes'],
        'stands': station['available_bike_stands'],
        'update': util.epoch_to_datetime(station['last_update'],
                                         divisor=1000).isoformat()
    }
    return [
        normalized(station)
        for station in stations
    ]
