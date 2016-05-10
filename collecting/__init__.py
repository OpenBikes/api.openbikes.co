from collecting.providers import *


def collect(provider, city):
    stations = eval(provider).stations(city)
    return stations
