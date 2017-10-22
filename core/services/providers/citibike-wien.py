import datetime as dt

import requests
import xmltodict

from core.services import station_updates

from .base import BaseProvider


class Provider(BaseProvider):

    def get_raw_updates(self, city_api_name=None) -> list:
        r = requests.get('http://dynamisch.citybikewien.at/citybike_xml.php')
        r.raise_for_status()
        return xmltodict.parse(r.content)['stations']['station']

    def parse_raw_update(self, raw_update: dict) -> station_updates.StationUpdate:
        return station_updates.StationUpdate(
            name=raw_update['name'],
            address=raw_update['description'],
            latitude=float(raw_update['latitude']),
            longitude=float(raw_update['longitude']),
            n_empty=int(raw_update['free_boxes']),
            n_taken=int(raw_update['free_bikes']),
            is_available=raw_update['status'] == 'aktiv',
            at=None,
        )
