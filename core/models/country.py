from django.db import models
from django.utils.text import slugify

from .base import BaseModel


class Country(BaseModel):
    name = models.TextField('Name', unique=True)

    class Meta:
        db_table = 't_countries'
        verbose_name_plural = 'countries'

    @property
    def slug(self):
        return slugify(self.name)
