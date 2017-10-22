from django.shortcuts import render

from core import models


def index(request):
    context = {}
    return render(request, 'core/index.html', context)


def archives(request):
    archived_city_ids = models.Archive.objects.values_list('city', flat=True).distinct()
    cities = models.City.objects\
        .select_related('country')\
        .select_related('provider')\
        .filter(id__in=archived_city_ids)\
        .order_by('country__name', 'name')
    context = {'cities': cities}
    return render(request, 'core/archives.html', context)


def city_archives(request, city_id):
    city = models.City.objects.filter(id=city_id).first()
    archives = models.Archive.objects\
        .filter(city__id=city_id)\
        .order_by('-year', '-month')
    context = {'city': city, 'archives': archives}
    return render(request, 'core/city_archives.html', context)
