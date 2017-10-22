import abc
import json

from django.conf import settings
import requests


class AltitudeService():
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def get_altitudes(self, latitudes: list, longitude: list) -> list:
        raise NotImplementedError


class DummyElevationService(AltitudeService):

    def get_altitudes(self, latitudes: list, longitudes: list) -> list:
        return [lat + lon for lat, lon in zip(latitudes, longitudes)]


class GoogleElevationService(AltitudeService):

    def __init__(self, batch_size=50):
        self.batch_size = batch_size

    def get_altitudes(self, latitudes: list, longitudes: list) -> list:

        # Fuse latitudes and longitudes
        points = [f'{lat},{lon}' for lat, lon in zip(latitudes, longitudes)]

        # Create batches the Google Elevation API can handle
        batches = [points[i:i + self.batch_size] for i in range(0, len(points), self.batch_size)]

        # Get the altitudes for each chunk
        base = 'https://maps.googleapis.com/maps/api/elevation/json?'
        api_key = settings.GOOGLE_ELEVATION_API_KEY
        results = []
        for batch in batches:
            locations = '|'.join(batch)
            url = f'{base}locations={locations}&key={api_key}'
            r = requests.get(url)
            r.raise_for_status()
            data = r.json()
            results.append(data['results'])

        # Extract altitudes
        altitudes = [result['elevation'] for result in sum(results, [])]

        return altitudes
