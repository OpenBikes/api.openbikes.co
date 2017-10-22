import os

from django.db import models
from django.conf import settings

from core import util

from .base import BaseModel
from .city import City


class Archive(BaseModel):
    year = models.IntegerField()
    month = models.IntegerField()
    n_bytes = models.BigIntegerField()

    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, related_name='archives')

    class Meta:
        db_table = 't_archives'
        verbose_name_plural = 'archives'

    @property
    def file_path(self):
        return os.path.join('archives', f'{self.city.slug}-{self.year}-{self.month:02d}.zip')

    @property
    def size(self):
        return util.humanize_n_bytes(self.n_bytes)
