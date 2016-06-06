from joblib import Parallel, delayed

from app import app
from app import logger
from app import models
from collecting import openweathermap as owm
from mongo.weather import insert as insert_weather


def fetch_data(city):
    '''
    Fetch the weather data for a city.
    '''
    # Get the current formatted data for a city
    try:
        weather = owm.current(city.name_owm)
    except:
        logger.warning("Couldn't retrieve weather data", city=city.name)
        return
    # Save the data for the map
    insert_weather.city(city.name, weather)


query = models.City.query.filter_by(active=True, predictable=True)
cities = query.all()

Parallel(n_jobs=2)(delayed(fetch_data)(city) for city in cities)
