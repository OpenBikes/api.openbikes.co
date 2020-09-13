from rest_framework import serializers

from . import models


class CitySerializer(serializers.ModelSerializer):
    country = serializers.CharField(source='country.name')
    provider = serializers.CharField(source='provider.name')

    class Meta:
        model = models.City
        fields = ('name', 'api_name', 'slug', 'active', 'provider', 'country', 'geojson')


class CountrySerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Country
        fields = ('name', 'slug')


class ProviderSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Provider
        fields = ('name', 'slug')
