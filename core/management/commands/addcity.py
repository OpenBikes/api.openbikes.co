from django.core.management.base import BaseCommand
from django.core.management.base import CommandError

from core import models
from core import services
from core.services import altitude
from core.services import time_zone
from core.services import station_updates
from core.services import weather


class Command(BaseCommand):
    help = 'Add a city'

    def add_arguments(self, parser):
        parser.add_argument('city', type=str)
        parser.add_argument('country', type=str)
        parser.add_argument('provider', type=str)
        parser.add_argument('api', type=str)

    def handle(self, *args, **options):

        city_name = options['city']
        country_name = options['country']
        provider_name = options['provider']
        city_api_name = options['api']

        # Instantiate services
        altitude_service = altitude.GoogleElevationService()
        station_updates_service = station_updates.OpenBikesService()
        time_zone_service = time_zone.GoogleTimeZoneService()
        weather_service = weather.OpenWeatherMapService()

        try:
            n_created_stations, country_added, provider_added = services.add_city(
                city_name=city_name,
                country_name=country_name,
                provider_name=provider_name,
                city_api_name=city_api_name,
                station_updates_service=station_updates_service,
                altitude_service=altitude_service,
                time_zone_service=time_zone_service,
                weather_service=weather_service,
            )
        except services.errors.CityAlreadyExists:
            raise CommandError(f'City "{city_name}" already exists')
        except (services.errors.UnknownProviderSlug, services.errors.ProviderNotImplemented):
            raise CommandError(f'Provider "{provider_name}" has no associated service')

        if country_added:
            self.stdout.write(self.style.SUCCESS(f'Successfully added country "{country_name}"'))

        if provider_added:
            self.stdout.write(self.style.SUCCESS(f'Successfully added provider "{provider_name}"'))

        message = f'Successfully added city "{city_name}" with {n_created_stations} stations'
        self.stdout.write(self.style.SUCCESS(message))
