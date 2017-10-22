import abc
import datetime as dt

from django.conf import settings
import pytz
import requests


class Weather():

    def __init__(self, at, pressure, temperature, humidity, wind_speed, clouds):
        self.at = at
        self.pressure = pressure
        self.temperature = temperature
        self.humidity = humidity
        self.wind_speed = wind_speed
        self.clouds = clouds


class WeatherService():
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def get_weather(self, latitude: float, longitude: float) -> Weather:
        raise NotImplementedError


class DummyWeatherService():

    def get_weather(self, latitude: float, longitude: float) -> Weather:
        return Weather(
            at=dt.datetime.now(),
            pressure=100,
            temperature=42,
            humidity=110,
            wind_speed=98,
            clouds=45
        )


class OpenWeatherMapService():

    def get_weather(self, latitude: float, longitude: float) -> Weather:
        url = f'http://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}'
        r = requests.get(
            url,
            params={
                'units': 'metric',
                'APPID': settings.OPEN_WEATHER_MAP_API_KEY
            }
        )
        r.raise_for_status()
        data = r.json()

        return Weather(
            at=pytz.utc.localize(dt.datetime.fromtimestamp(data['dt'])),
            pressure=data['main']['pressure'],
            temperature=data['main']['temp'],
            humidity=data['main']['humidity'],
            wind_speed=data['wind']['speed'],
            clouds=data['clouds']['all']
        )
