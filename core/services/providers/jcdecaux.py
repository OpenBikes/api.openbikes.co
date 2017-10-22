import datetime as dt

from django.conf import settings
import requests

from core.services import station_updates

from .base import BaseProvider


class Provider(BaseProvider):

    def get_raw_updates(self, city_api_name=None) -> list:
        r = requests.get(
            'https://api.jcdecaux.com/vls/v1/stations',
            params={
                'contract': city_api_name,
                'apiKey': settings.JCDECAUX_API_KEY
            }
        )
        r.raise_for_status()
        return r.json()

    def parse_raw_update(self, raw_update: dict) -> station_updates.StationUpdate:
        return station_updates.StationUpdate(
            name=raw_update['name'],
            address=raw_update['address'],
            latitude=raw_update['position']['lat'],
            longitude=raw_update['position']['lng'],
            n_empty=raw_update['available_bike_stands'],
            n_taken=raw_update['available_bikes'],
            is_available=raw_update['status'] == 'OPEN',
            at=dt.datetime.fromtimestamp(raw_update['last_update'] / 1000)
        )
