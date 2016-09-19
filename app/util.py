import math
import re
from string import punctuation
import time
from unidecode import unidecode

from werkzeug.routing import NumberConverter


class FloatConverter(NumberConverter):

    """ This converter supports negative values.
    The built-in FloatConverter does not handle negative numbers. So we need to
    write a custom converter to handle negatives. This converter also treats
    integers as floats, which also would have failed.

    Args: see werkeuz.routing docstring (http://werkzeug.pocoo.org/docs/0.11/routing/#werkzeug.routing.FloatConverter)
        map: the :class: `Map`
        min: the minimal value
        max: the maximal value
    """

    regex = r'-?\d+(\.\d+)?'
    num_convert = float

    def __init__(self, map, min=None, max=None):
        NumberConverter.__init__(self, map, 0, min, max)


def compute_haversine_distance(lat1, lon1, lat2, lon2):
    # Convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, (lat1, lon2, lat2, lon2))
    # Apply Haversine formula
    a = (math.sin((lat2 - lat1) / 2) ** 2 +
         math.cos(lat1) * math.cos(lat2) * math.sin((lon2 - lon1) / 2) ** 2)
    c = 2 * math.asin(math.sqrt(a))
    # 6371000 meters is the mean radius of the Earth
    return 6371000 * c


def slugify(string):
    '''
    Slugify a string. For example "Hello world!" becomes "hello-world"

    - Punctuation is removed.
    - White spaces are replaced by a hyphen.
    - Letters are lowercased.

    Args:
        string (str): The string to slugify.

    Returns:
        dict: The latest geojson file.
    '''
    # Lowercase
    string = string.lower()
    # Convert to ASCII characters
    string = unidecode(string)
    # Remove punctuation except for hyphens
    puncs = punctuation.replace('-', '')
    for punc in puncs:
        string = string.replace(punc, '')
    # Replace spaces with a single hyphen
    string = re.sub(r'\s+', '-', string)
    # Replace multiple hyphens with a single hyphen
    string = re.sub(r'\-+', '-', string)
    # Remove trailing hyphens
    string = string.strip('-')
    return string


def timethisfunc(func):
    def wrapper(*arg, **kw):
        t1 = time.time()
        res = func(*arg, **kw)
        t2 = time.time()
        return (t2 - t1), res, func.__name__
    return wrapper
