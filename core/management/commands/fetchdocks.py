from concurrent import futures
import logging

from django.core.management.base import BaseCommand
from django.core.management.base import CommandError

from core import models
from core import services
from core.services import altitude
from core.services import station_updates


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Fetch docks updates'

    def add_arguments(self, parser):
        parser.add_argument('cities', nargs='+', type=str)
        parser.add_argument('n_threads', type=int)

    def handle(self, *args, **options):

        city_names = options['cities']
        n_threads = options['n_threads']

        if city_names[0] == 'ALL':
            city_names = services.get_active_city_names()

        # Instantiate services
        station_updates_service = station_updates.OpenBikesService()
        altitude_service = altitude.GoogleElevationService()

        def fetch_docks(city_name):
            try:
                n_new_updates, n_new_stations = services.fetch_docks_updates(
                    city_name=city_name,
                    station_updates_service=station_updates_service,
                    altitude_service=altitude_service
                )
            except services.errors.CityNotFound:
                return self.style.ERROR(f'City "{city_name}" does not exist')
            except services.errors.CityIsDisabled:
                return self.style.ERROR(f'City "{city_name}" is disabled')
            except requests.exceptions.HTTPError:
                return self.style.ERROR(f'Error querying API for city "{city_name}"')
            return self.style.SUCCESS(f'Successfully fetched {n_new_updates} new update(s) and ' + \
                                      f'added {n_new_stations} new station(s) for city ' + \
                                      f'"{city_name}"')

        pool = futures.ThreadPoolExecutor(n_threads)
        jobs = []

        for city_name in city_names:
            jobs.append(pool.submit(fetch_docks, city_name))

        for job in futures.as_completed(jobs):
            self.stdout.write(job.result())
