import datetime as dt

import requests
import xmltodict

from core.services import station_updates

from .base import BaseProvider


class Provider(BaseProvider):

    def get_raw_updates(self, city_name) -> list:
        r = requests.get('http://minaport.ubweb.jp/stations.php')
        r.raise_for_status()
        return xmltodict.parse(r.content)['markers']['marker']

    def parse_raw_update(self, raw_update: dict) -> station_updates.StationUpdate:
        return station_updates.StationUpdate(
            name=raw_update['@stname'],
            address=raw_update['@staddr'],
            latitude=float(raw_update['@stlat']),
            longitude=float(raw_update['@stlng']),
            n_empty=int(raw_update['@stat2']),
            n_taken=int(raw_update['@stat1']),
            is_available=raw_update['@stat1'] != '0' or raw_update['@stat2'] != '0',
            at=dt.datetime.strptime(raw_update['@date'], '%Y-%m-%d %H:%M:%S')
        )
