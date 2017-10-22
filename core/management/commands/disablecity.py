from django.core.management.base import BaseCommand
from django.core.management.base import CommandError

from core import services


class Command(BaseCommand):
    help = 'Disable a city'

    def add_arguments(self, parser):
        parser.add_argument('city', type=str)

    def handle(self, *args, **options):

        city_name = options['city']

        try:
            services.disable_city(city_name=city_name)
        except services.errors.CityNotFound:
            raise CommandError(f'City "{city_name}" does not exist')
        except services.errors.CityIsDisabled:
            self.stdout.write(self.style.WARNING(f'City "{city_name}" is already disabled'))
            return

        self.stdout.write(self.style.SUCCESS(f'Successfully disabled city "{city_name}"'))
