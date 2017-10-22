import datetime as dt

import requests

from core.services import station_updates

from .base import BaseProvider


class Provider(BaseProvider):

    def get_raw_updates(self, city_api_name=None) -> list:
        r = requests.get('http://www.bayareabikeshare.com/stations/json')
        r.raise_for_status()
        return r.json()['stationBeanList']

    def parse_raw_update(self, raw_update: dict) -> station_updates.StationUpdate:
        return station_updates.StationUpdate(
            name=raw_update['stationName'],
            address=raw_update['stAddress1'],
            latitude=raw_update['latitude'],
            longitude=raw_update['longitude'],
            n_empty=raw_update['availableDocks'],
            n_taken=raw_update['availableBikes'],
            is_available=raw_update['statusValue'] == 'In Service',
            at=dt.datetime.strptime(raw_update['lastCommunicationTime'], '%Y-%m-%d %I:%M:%S %p')
        )
