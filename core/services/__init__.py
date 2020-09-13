import csv
import datetime as dt
import io
import json
import os
import zipfile

from django.conf import settings
from django.db import transaction
from django.utils import timezone
import pytz

from core import models

from . import errors
from . import geojson
from .altitude import AltitudeService
from .time_zone import TimeZoneService
from .station_updates import StationUpdatesService
from .weather import WeatherService


@transaction.atomic
def add_city(city_name: str,
             country_name: str,
             provider_name: str,
             city_api_name: str,
             station_updates_service: StationUpdatesService,
             altitude_service: AltitudeService,
             time_zone_service: TimeZoneService,
             weather_service: WeatherService) -> int:

    # Check if the city has already been added
    if models.City.objects.filter(name=city_name).exists():
        raise errors.CityAlreadyExists

    # Check if the country exists
    country_q = models.Country.objects.filter(name=country_name)
    country_exists = country_q.exists()
    if not country_exists:
        models.Country(name=country_name).save()
    country = country_q.first()

    # Check if the provider exists
    provider_q = models.Provider.objects.filter(name=provider_name)
    provider_exists = provider_q.exists()
    if not provider_exists:
        models.Provider(name=provider_name).save()
    provider = provider_q.first()

    # Get station updates for the given city and provider
    station_updates = list(station_updates_service.get_updates(city_api_name, provider_name))
    station_updates_fetched_at = timezone.now()

    # Get station altitudes
    latitudes = [su.latitude for su in station_updates]
    longitudes = [su.longitude for su in station_updates]
    altitudes = altitude_service.get_altitudes(latitudes=latitudes, longitudes=longitudes)

    # Get city weather update
    avg_latitude = sum(latitudes) / len(latitudes)
    avg_longitude = sum(longitudes) / len(longitudes)
    weather = weather_service.get_weather(latitude=avg_latitude, longitude=avg_longitude)
    weather_fetched_at = timezone.now()

    # Get city time zone
    time_zone = time_zone_service.get_time_zone(latitude=avg_latitude, longitude=avg_longitude)
    tz = pytz.timezone(time_zone)

    # Instantiate stations
    stations = [
        models.Station(
            name=station_update.name,
            latitude=station_update.latitude,
            longitude=station_update.longitude,
            altitude=altitude,
            is_available=station_update.is_available
        )
        for station_update, altitude in zip(station_updates, altitudes)
    ]

    # Save city
    city = models.City(
        name=city_name,
        api_name=city_api_name,
        active=True,
        time_zone=time_zone,
        country=country,
        provider=provider
    )
    city.save()

    # Save weather update
    weather_update = models.WeatherUpdate(
        fetched_at=weather_fetched_at,
        at=weather.at,
        pressure=weather.pressure,
        temperature=weather.temperature,
        humidity=weather.humidity,
        wind_speed=weather.wind_speed,
        clouds=weather.clouds,
        city=city
    )
    weather_update.save()

    # Save stations
    for station in stations:
        station.city = city
        station.save()

    # Save docks updates
    docks_updates = [
        models.DocksUpdate(
            fetched_at=station_updates_fetched_at,
            at=tz.localize(su.at) if su.at else None,
            n_empty=su.n_empty,
            n_taken=su.n_taken,
            station=station
        )
        for su, station in zip(station_updates, stations)
    ]

    # Add docks updates to stations
    for station, docks_update in zip(stations, docks_updates):
        docks_update.save()
        station.docks_update = docks_update
        station.save()

    # Add geojson to city
    city._geojson = json.dumps(geojson.convert_stations_to_geojson(stations))
    city.save()

    # Add weather to city
    city.weather_update = weather_update
    city.save()

    # Return the number of created stations
    return len(stations), not country_exists, not provider_exists


@transaction.atomic
def remove_city(city_name: str) -> (str, str):

    # Check if the city exists
    city_q = models.City.objects.filter(name=city_name)
    if not city_q.exists():
        raise errors.CityNotFound

    # Delete the city
    city = city_q.first()
    city.delete()

    # Check if the country should be deleted
    country = city.country
    country_is_empty = country.cities.count() == 0
    if country_is_empty:
        country.delete()

    # Check if the provider should be deleted
    provider = city.provider
    provider_is_empty = provider.cities.count() == 0
    if provider_is_empty:
        provider.delete()

    return (
        country.name if country_is_empty else None,
        provider.name if provider_is_empty else None
    )


@transaction.atomic
def disable_city(city_name: str):

    # Check if the city exists
    city_q = models.City.objects.filter(name=city_name)
    if not city_q.exists():
        raise errors.CityNotFound

    # Check if the city is already disabled
    city = city_q.first()
    if not city.active:
        raise errors.CityIsDisabled

    # Disable the city
    city.active = False
    city.save()


@transaction.atomic
def enable_city(city_name: str):

    # Check if the city exists
    city_q = models.City.objects.filter(name=city_name)
    if not city_q.exists():
        raise errors.CityNotFound

    # Check if the city is already enabled
    city = city_q.first()
    if city.active:
        raise errors.CityIsEnabled

    # Enable the city
    city.active = True
    city.save()


def get_active_city_names() -> list:
    cities = models.City.objects.filter(active=True)
    return [city.name for city in cities]


@transaction.atomic
def fetch_docks_updates(city_name: str,
                        station_updates_service: StationUpdatesService,
                        altitude_service: AltitudeService) -> int:

    # Check if the city exists
    city_q = models.City.objects.filter(name=city_name)
    if not city_q.exists():
        raise errors.CityNotFound

    # Check if the city is enabled
    city = city_q.first()
    if not city.active:
        raise errors.CityIsDisabled

    # Determine the time zone
    tz = pytz.timezone(city.time_zone)

    # Get the city's stations
    stations = {
        station.name: station
        for station in city.stations.select_related('docks_update').all()
    }

    # Get the latest updates
    station_updates = station_updates_service.get_updates(city.api_name, city.provider.name)
    fetched_at = timezone.now()

    # Track the number of new updates
    n_new_updates = 0
    n_new_stations = 0
    n_availability_changes = 0

    # For each update check if it is new or not
    for su in station_updates:

        # Get the matching station
        station = stations.get(su.name)

        # If the station doesn't exist then add it
        if not station:
            altitude = altitude_service.get_altitudes([su.latitude], [su.longitude])[0]
            station = models.Station(
                name=su.name,
                latitude=su.latitude,
                longitude=su.longitude,
                altitude=altitude,
                is_available=su.is_available,
                city=city
            )
            station.save()
            docks_update = models.DocksUpdate(
                fetched_at=fetched_at,
                at=tz.localize(su.at) if su.at else None,
                n_empty=su.n_empty,
                n_taken=su.n_taken,
                station=station
            )
            docks_update.save()
            station.docks_update = docks_update
            station.save()
            stations[station.name] = station
            n_new_stations += 1
            continue

        # Check if the station' availability has changed
        if su.is_available != station.is_available:
            station.is_available = su.is_available
            station.save()
            n_availability_changes += 1

        # Check if something has changed
        docks_have_changed = (
            not station.docks_update or
            su.n_empty != station.docks_update.n_empty or
            su.n_taken != station.docks_update.n_taken
        )

        # Update information if something has changed
        if docks_have_changed:

            # Add a docks updates
            docks_update = models.DocksUpdate(
                fetched_at=fetched_at,
                at=tz.localize(su.at) if su.at else None,
                n_empty=su.n_empty,
                n_taken=su.n_taken,
                station=station
            )
            docks_update.save()

            # Update the station information
            station.docks_update = docks_update
            station.is_available = su.is_available
            station.save()

            n_new_updates += 1

    # Update city geojson if there has been any new updates or any new stations
    if n_new_updates > 0 or n_new_stations > 0  or n_availability_changes > 0:
        city._geojson = json.dumps(geojson.convert_stations_to_geojson(stations.values()))
        city.save()

    return n_new_updates, n_new_stations


@transaction.atomic
def fetch_weather_update(city_name: str, weather_service: WeatherService) -> bool:

    # Check if the city exists
    city_q = models.City.objects.filter(name=city_name)
    if not city_q.exists():
        raise errors.CityNotFound

    # Check if the city is enabled
    city = city_q.first()
    if not city.active:
        raise errors.CityIsDisabled

    # Get the mean latitude and longitude
    stations = city.stations.all()
    avg_latitude = 0
    avg_longitude = 0
    for station in stations:
        avg_latitude += station.latitude
        avg_longitude += station.longitude
    avg_latitude /= len(stations)
    avg_longitude /= len(stations)

    # Get the latest weather
    weather = weather_service.get_weather(latitude=avg_latitude, longitude=avg_longitude)
    fetched_at = timezone.now()

    # Check if weather is new or not
    if city.weather_update and weather.at <= city.weather_update.at:
        return False

    # Save weather update
    weather_update = models.WeatherUpdate(
        fetched_at=fetched_at,
        at=weather.at,
        pressure=weather.pressure,
        temperature=weather.temperature,
        humidity=weather.humidity,
        wind_speed=weather.wind_speed,
        clouds=weather.clouds,
        city=city
    )
    weather_update.save()

    # Update city weather
    city.weather_update = weather_update
    city.save()

    return True


@transaction.atomic
def make_archive(city_name: str, year: int, month: int) -> float:

    # Check if the city exists
    city_q = models.City.objects.filter(name=city_name)
    if not city_q.exists():
        raise errors.CityNotFound
    city = city_q.first()

    # Check if the archive exists
    if models.Archive.objects.filter(year=year, month=month, city=city).exists():
        raise errors.ArchiveAlreadyExists

    # Determine the city's time zone
    tz = pytz.timezone(city.time_zone)

    # Get the docks updates
    docks_updates_q = models.DocksUpdate.objects.filter(
        at__year=year,
        at__month=month,
        station__city=city
    ).select_related('station')
    docks_updates = docks_updates_q.all()

    # Take into account the city's time zone
    for docks_update in docks_updates:
        docks_update.fetched_at = docks_update.fetched_at.astimezone(tz)
        docks_update.at = docks_update.at.astimezone(tz)

    # Get the list of stations associated with the docks updates
    stations = list(set([docks_update.station for docks_update in docks_updates]))

    # Get the weather updates
    weather_updates_q = models.WeatherUpdate.objects.filter(city=city)
    weather_updates = weather_updates_q.all()

    # Take into account the city's time zone
    for weather_update in weather_updates:
        weather_update.fetched_at = weather_update.fetched_at.astimezone(tz)
        weather_update.at = weather_update.at.astimezone(tz)

    # Create an archive instance
    archive = models.Archive(
        year=year,
        month=month,
        city=city
    )

    file_path = os.path.join(settings.MEDIA_ROOT, archive.file_path)
    file_name = file_path.split('/')[-1].split('.')[0]
    dir_name = '/'.join(file_path.split('/')[:-1])
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)

    with zipfile.ZipFile(f'{file_path}', 'w', zipfile.ZIP_DEFLATED) as z:

        # Save stations information
        sb = io.StringIO()
        w = csv.writer(sb)
        w.writerow(('name', 'slug', 'latitude', 'longitude', 'altitude'))
        for s in sorted(stations, key=lambda x: x.name):
            w.writerow((s.name, s.slug, s.latitude, s.longitude, s.altitude))
        z.writestr(f'{file_name}/stations.csv', sb.getvalue())

        # Save docks updates
        for s in stations:
            sb = io.StringIO()
            w = csv.writer(sb)
            docks = [du for du in docks_updates if du.station.name == s.name]
            w.writerow(('at', 'n_empty', 'n_taken'))
            for d in sorted(docks, key=lambda x: x.at):
                w.writerow((d.at, d.n_empty, d.n_taken))
            z.writestr(f'{file_name}/docks/{s.slug}.csv', sb.getvalue())

        # Save weather
        sb = io.StringIO()
        w = csv.writer(sb)
        w.writerow(('at', 'pressure', 'temperature', 'humidity', 'wind_speed', 'clouds'))
        for u in sorted(weather_updates, key=lambda x: x.at):
            w.writerow((u.at, u.pressure, u.temperature, u.humidity, u.wind_speed, u.clouds))
        z.writestr(f'{file_name}/weather.csv', sb.getvalue())

    # Update the archive's file size
    archive.n_bytes = os.path.getsize(file_path)
    archive.save()

    # Delete the docks updates
    docks_updates_q.delete()

    # Delete the weather updates
    weather_updates_q.delete()

    return os.path.getsize(file_path)
