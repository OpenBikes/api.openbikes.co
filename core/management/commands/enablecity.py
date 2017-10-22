from django.core.management.base import BaseCommand
from django.core.management.base import CommandError

from core import services


class Command(BaseCommand):
    help = 'Enable a city'

    def add_arguments(self, parser):
        parser.add_argument('city', type=str)

    def handle(self, *args, **options):

        city_name = options['city']

        try:
            services.enable_city(city_name=city_name)
        except services.errors.CityNotFound:
            raise CommandError(f'City "{city_name}" does not exist')
        except services.errors.CityIsEnabled:
            self.stdout.write(self.style.WARNING(f'City "{city_name}" is already enabled'))
            return

        self.stdout.write(self.style.SUCCESS(f'Successfully enabled city "{city_name}"'))
