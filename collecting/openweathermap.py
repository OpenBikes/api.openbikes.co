import datetime as dt
import requests


def current(city):
    '''
    Collect the weather data for a city. The city parameter corresponds to the
    name of the city in the OpenWeatherMap database, this makes results more
    reliable.
    '''
    payload = {
        'q': city,
        'units': 'metric',
        'APPID': os.environ.get('OPEN_WEATHER_MAP_API_KEY')
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
        'temperature': round(data['main']['temp'], 2),
        'humidity': data['main']['humidity'],
        'wind_speed': round(data['wind']['speed'], 2),
        'clouds': data['clouds']['all']
    }
    return weather
