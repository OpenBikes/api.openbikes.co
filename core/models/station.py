from django.db import models
from django.utils.text import slugify

from .base import BaseModel
from .city import City
from .docks_update import DocksUpdate


class Station(BaseModel):
    name = models.TextField('Name')
    slug = models.TextField('Slug')
    latitude = models.FloatField()
    longitude = models.FloatField()
    altitude = models.FloatField()
    is_available = models.BooleanField(default=True)

    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='stations')
    docks_update = models.OneToOneField(DocksUpdate, on_delete=models.SET_NULL, null=True,
                                        related_name='stations')

    class Meta:
        db_table = 't_stations'
        verbose_name_plural = 'stations'

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)
