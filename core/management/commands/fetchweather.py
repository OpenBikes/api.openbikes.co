from concurrent import futures

from django.core.management.base import BaseCommand
from django.core.management.base import CommandError

from core import models
from core import services
from core.services import weather


class Command(BaseCommand):
    help = 'Fetch weather updates'

    def add_arguments(self, parser):
        parser.add_argument('cities', nargs='+', type=str)
        parser.add_argument('n_threads', type=int)

    def handle(self, *args, **options):

        city_names = options['cities']
        n_threads = options['n_threads']

        if city_names[0] == 'ALL':
            city_names = services.get_active_city_names()

        # Instantiate weather service
        weather_service = weather.OpenWeatherMapService()

        def fetch_weather_update(city_name):
            try:
                made_update = services.fetch_weather_update(city_name=city_name,
                                                            weather_service=weather_service)
            except services.errors.CityNotFound:
                return self.style.ERROR(f'City "{city_name}" does not exist')
            except services.errors.CityIsDisabled:
                return self.style.ERROR(f'City "{city_name}" is disabled')
            if made_update:
                return self.style.SUCCESS('Successfully fetched new weather update for city ' + \
                                          f'"{city_name}"')
            else:
                return self.style.WARNING(f'No new weather update found for city "{city_name}"')

        pool = futures.ThreadPoolExecutor(n_threads)
        jobs = []

        for city_name in city_names:
            jobs.append(pool.submit(fetch_weather_update, city_name))

        for job in futures.as_completed(jobs):
            self.stdout.write(job.result())
