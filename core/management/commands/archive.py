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
        parser.add_argument('city', type=str)
        parser.add_argument('year', type=int)
        parser.add_argument('month', type=int)

    def handle(self, *args, **options):

        city_name = options['city']
        year = options['year']
        month = options['month']

        try:
            n_bytes = services.make_archive(
                city_name=city_name,
                year=year,
                month=month
            )
        except services.errors.CityNotFound:
            raise CommandError(f'City "{city_name}" does not exist')
        except services.errors.ArchiveAlreadyExists:
            message = f'{year}-{month:02d} data has already been archived for city "{city_name}"'
            raise CommandError(message)

        message = f'Successfully archived {year}-{month:02d} data for city "{city_name}" ' + \
                  f'({util.humanize_n_bytes(n_bytes)})'
        self.stdout.write(self.style.SUCCESS(message))
