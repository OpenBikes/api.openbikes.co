import json

from django.db import models
from django.utils.text import slugify

from .base import BaseModel
from .country import Country
from .provider import Provider
from .weather_update import WeatherUpdate


class City(BaseModel):
    name = models.TextField('Name', unique=True)
    slug = models.TextField('Slug', unique=True)
    api_name = models.TextField('API name', null=True)
    active = models.BooleanField(default=True)
    time_zone = models.TextField('Time zone')
    _geojson = models.TextField('GeoJSON', null=True)

    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='cities')
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE, related_name='cities')
    weather_update = models.OneToOneField(WeatherUpdate, on_delete=models.SET_NULL, null=True,
                                          related_name='cities')

    class Meta:
        db_table = 't_cities'
        verbose_name_plural = 'cities'

    @property
    def geojson(self):
        return json.loads(self._geojson)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)
