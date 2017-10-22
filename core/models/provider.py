from django.db import models
from django.utils.text import slugify

from .base import BaseModel


class Provider(BaseModel):
    name = models.TextField('Name', unique=True)

    class Meta:
        db_table = 't_providers'
        verbose_name_plural = 'providers'

    @property
    def slug(self):
        return slugify(self.name)
