import datetime as dt

import requests
import xmltodict

from core.services import station_updates

from .base import BaseProvider


class Provider(BaseProvider):

    def get_raw_updates(self, city_api_name=None) -> list:
        r = requests.get('http://www.thehubway.com/data/stations/bikeStations.xml')
        r.raise_for_status()
        return xmltodict.parse(r.content)['stations']['station']

    def parse_raw_update(self, raw_update: dict) -> station_updates.StationUpdate:
        return station_updates.StationUpdate(
            name=raw_update['name'],
            address=raw_update['name'],
            latitude=raw_update['lat'],
            longitude=raw_update['long'],
            n_empty=raw_update['nbEmptyDocks'],
            n_taken=raw_update['nbBikes'],
            is_available=raw_update['locked'] == 'false',
            at=dt.datetime.utcfromtimestamp(int(raw_update['latestUpdateTime']) / 1000)
        )
