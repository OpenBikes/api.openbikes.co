from django.db import models
from django.utils.text import slugify

from .base import BaseUpdate


class DocksUpdate(BaseUpdate):
    at = models.DateTimeField(null=True)
    n_empty = models.IntegerField()
    n_taken = models.IntegerField()

    station = models.ForeignKey('core.Station', on_delete=models.CASCADE, related_name='updates')

    class Meta:
        db_table = 't_docks_updates'
        verbose_name_plural = 'docks_updates'
