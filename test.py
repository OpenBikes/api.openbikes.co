import datetime as dt

from app import models

city = models.City.query.first()

print(city.get_weather_updates(dt.datetime(year=1900, month=1, day=1), dt.datetime.now()))
