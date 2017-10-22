from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.response import Response

from . import models
from . import serializers


class CityViewSet(viewsets.ViewSet):

    def list(self, request):
        queryset = models.City.objects.all()
        serializer = serializers.CitySerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        city = get_object_or_404(models.City.objects.all(), pk=pk)
        serializer = serializers.CitySerializer(city)
        return Response(serializer.data)
