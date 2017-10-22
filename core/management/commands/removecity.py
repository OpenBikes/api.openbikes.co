from django.core.management.base import BaseCommand
from django.core.management.base import CommandError

from core import services


class Command(BaseCommand):
    help = 'Remove a city'

    def add_arguments(self, parser):
        parser.add_argument('city', type=str)

    def handle(self, *args, **options):

        city_name = options['city']

        try:
            removed_country, removed_provider = services.remove_city(city_name=city_name)
        except services.errors.CityNotFound:
            raise CommandError(f'City "{city_name}" does not exist')

        self.stdout.write(self.style.WARNING(f'Successfully removed city "{city_name}"'))

        if removed_country:
            message = f'Successfully removed country "{removed_country}"'
            self.stdout.write(self.style.WARNING(message))

        if removed_provider:
            message = f'Successfully removed provider "{removed_provider}"'
            self.stdout.write(self.style.WARNING(message))
