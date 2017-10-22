from django.db import models
from django.utils.text import slugify

from .base import BaseUpdate


class WeatherUpdate(BaseUpdate):
    at = models.DateTimeField()
    pressure = models.FloatField()
    temperature = models.FloatField()
    humidity = models.FloatField()
    wind_speed = models.FloatField()
    clouds = models.FloatField()

    city = models.ForeignKey('core.City', null=True, on_delete=models.CASCADE,
                             related_name='weather_updates')

    class Meta:
        db_table = 't_weather_updates'
        verbose_name_plural = 'weather_updates'
