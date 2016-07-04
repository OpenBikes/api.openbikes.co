import re
from string import punctuation
import time
from unidecode import unidecode


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
    # Remove punctuation except hyphens
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
