import abc

from core.services import station_updates


class BaseProvider():
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def get_raw_updates(self, city_api_name=None) -> list:
        raise NotImplementedError

    @abc.abstractmethod
    def parse_raw_update(self, raw_update: dict) -> station_updates.StationUpdate:
        raise NotImplementedError

    def fetch(self, city_api_name):
        for raw_update in self.get_raw_updates(city_api_name):
            yield self.parse_raw_update(raw_update)
