from django.db import models
from django.utils.text import slugify

from .base import BaseModel


class Provider(BaseModel):
    name = models.TextField('Name', unique=True)
    slug = models.TextField('Slug', unique=True)

    class Meta:
        db_table = 't_providers'
        verbose_name_plural = 'providers'

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)
