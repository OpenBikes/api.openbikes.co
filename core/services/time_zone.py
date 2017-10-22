import abc
import datetime as dt

from django.conf import settings
import requests


class TimeZoneService():
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def get_time_zone(self, latitude: float, longitude: float) -> str:
        raise NotImplementedError


class DummyTimeZoneService(TimeZoneService):

    def get_time_zone(self, latitude: float, longitude: float, ) -> str:
        return 'Europe/Paris'


class GoogleTimeZoneService(TimeZoneService):

    def get_time_zone(self, latitude: float, longitude: float) -> str:

        base = 'https://maps.googleapis.com/maps/api/timezone/json?'
        api_key = settings.GOOGLE_ELEVATION_API_KEY
        timestamp = dt.datetime.now().timestamp()
        url = f'{base}location={latitude},{longitude}&timestamp={timestamp}&key={api_key}'
        r = requests.get(url)
        r.raise_for_status()
        data = r.json()

        return data['timeZoneId']
