import datetime as dt

import requests

from app import app


def current(city):
    '''
    Collect the weather data for a city. The city parameter corresponds to the
    name of the city in the OpenWeatherMap database, this makes results more
    reliable.
    '''
    payload = {
        'q': city,
        'units': 'metric',
        'APPID': app.config['OPEN_WEATHER_MAP_API_KEY']
    }
    response = requests.get(
        'http://api.openweathermap.org/data/2.5/weather',
        params=payload
    )
    data = response.json()
    weather = {
        'datetime': dt.datetime.fromtimestamp(data['dt']),
        'pressure': data['main']['pressure'],
        'description': data['weather'][0]['description'],
        'temperature': data['main']['temp'],
        'humidity': data['main']['humidity'],
        'wind_speed': data['wind']['speed'],
        'clouds': data['clouds']['all']
    }
    return weather
