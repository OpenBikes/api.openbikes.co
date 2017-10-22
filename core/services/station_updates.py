import abc
import importlib

from django.utils.text import slugify

from . import errors


class StationUpdate():

    def __init__(self, name, address, latitude, longitude, n_empty, n_taken, is_available, at):
        self.name = name
        self.address = address
        self.latitude = latitude
        self.longitude = longitude
        self.n_empty = n_empty
        self.n_taken = n_taken
        self.is_available = is_available
        self.at = at


class StationUpdatesService():
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def get_updates(self, city_name: str, provider_name: str) -> list:
        raise NotImplementedError


class OpenBikesService(StationUpdatesService):

    def get_updates(self, city_name: str, provider_name: str) -> list:
        # Get provider
        provider_name_slug = slugify(provider_name)

        try:
            module = importlib.import_module(f'core.services.providers.{provider_name_slug}')
        except ModuleNotFoundError:
            raise errors.UnknownProviderSlug

        try:
            provider = getattr(module, 'Provider')()
        except AttributeError:
            raise errors.ProviderNotImplemented

        return provider.fetch(city_name)
