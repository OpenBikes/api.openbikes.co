from django.shortcuts import get_object_or_404
import django_filters.rest_framework
from rest_framework import viewsets

from . import models
from . import serializers


class CityViewSet(viewsets.ModelViewSet):
    queryset = models.City.objects
    serializer_class = serializers.CitySerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    filter_fields = ('name', 'api_name', 'slug', 'active', 'provider', 'country')


class CountryViewSet(viewsets.ModelViewSet):
    queryset = models.Country.objects
    serializer_class = serializers.CountrySerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    filter_fields = ('name', 'slug')


class ProviderViewSet(viewsets.ModelViewSet):
    queryset = models.Provider.objects
    serializer_class = serializers.ProviderSerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    filter_fields = ('name', 'slug')
