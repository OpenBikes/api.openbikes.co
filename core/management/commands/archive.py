from django.core.management.base import BaseCommand
from django.core.management.base import CommandError

from core import models
from core import services
from core import util
from core.services import altitude
from core.services import station_updates
from core.services import weather


class Command(BaseCommand):
    help = "Archive a month of a city's data"

    def add_arguments(self, parser):
        parser.add_argument('year', type=int)
        parser.add_argument('month', type=int)
        parser.add_argument('cities', nargs='+', type=str)

    def handle(self, *args, **options):

        year = options['year']
        month = options['month']
        city_names = options['cities']

        if city_names[0] == 'ALL':
            city_names = services.get_active_city_names()

        def make_archive(city_name, year, month):
            try:
                n_bytes = services.make_archive(
                    city_name=city_name,
                    year=year,
                    month=month
                )
            except services.errors.CityNotFound:
                return self.style.ERROR(f'City "{city_name}" does not exist')
            except services.errors.ArchiveAlreadyExists:
                message = f'{year}-{month:02d} data has already been archived for city "{city_name}"'
                return self.style.ERROR(message)
            message = f'Successfully archived {year}-{month:02d} data for city "{city_name}" ' + \
                      f'({util.humanize_n_bytes(n_bytes)})'
            return self.style.SUCCESS(message)

        for city_name in city_names:
            make_archive(city_name)
