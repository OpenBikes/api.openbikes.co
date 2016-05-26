import os
import glob
import json
import datetime as dt

from scipy.stats import norm

from app import app
from app import models
from app.exceptions import (
    CityNotFound,
    CityInactive,
    CityUnpredicable,
    StationNotFound,
    InvalidKind,
    PastTimestamp
)
from collecting import google


def geojson(city):
    '''
    Open and return the latest geojson file of a city as a dictionary.

    Args:
        city (str): The city name.

    Returns:
        dict: The latest geojson file.

    Raises:
        CityNotFound: The geojson file cannot be found.
    '''
    path = os.path.join(app.config['GEOJSON_FOLDER'], '{}.geojson'.format(city))
    try:
        with open(path, 'r') as infile:
            return json.loads(infile.read())
    except:
        raise CityNotFound("'{}' not found".format(city))


def get_countries(name=None, provider=None, as_query=False):
    '''
    Filter and return a dictionary or query of countries.

    Args:
        name (str): A country name.
        provider (str): A data provider name.

    Returns:
        generator(dict) or query: The countries.
    '''
    # Restrict the returned fields
    query = models.City.query.with_entities(
        models.City.country,
        models.City.provider
    )

    # Filter on the country name
    if name:
        query = query.filter_by(country=name)

    # Filter on the data provider
    if provider:
        query = query.filter_by(provider=provider)

    if as_query:
        return query
    else:
        countries = query.all()
        return (country._asdict() for country in countries)


def get_providers(name=None, country=None, as_query=False):
    '''
    Filter and return a dictionary or query of providers.

    Args:
        name (str): A provider name.
        country (str): A country name.

    Returns:
        generator(dict) or query: The providers.
    '''
    # Restrict the returned fields
    query = models.City.query.with_entities(
        models.City.provider,
        models.City.country
    )

    # Filter on the provider name
    if name:
        query = query.filter_by(provider=name)

    # Filter on the country name
    if country:
        query = query.filter_by(country=country)

    if as_query:
        return query
    else:
        providers = query.all()
        return (provider._asdict() for provider in providers)


def get_cities(name=None, country=None, provider=None, predictable=None, active=None, as_query=False):
    '''
    Filter and return a dictionary or query of cities.

    Args:
        name (str): A city name.
        country (str): A country name.
        provider (str): A data provider name.
        predicable (bool): An indicator if the city is predicable or not.
        active (bool): An indicator if the city is active or not.
        as_query (bool): Return the query object or a generator.

    Returns:
        generator(dict) or query: The cities.
    '''
    # Restrict the returned fields
    query = models.City.query.with_entities(
        models.City.name,
        models.City.latitude,
        models.City.longitude,
        models.City.predictable,
        models.City.active,
        models.City.country,
        models.City.provider
    )

    # Filter on the city name
    if name:
        query = query.filter_by(name=name)

    # Filter if predictions are available or not
    if predictable:
        query = query.filter_by(predictable=predictable)

    # Filter if the city is active or not
    if active:
        query = query.filter_by(active=active)

    # Filter on the belonging country
    if country:
        query = query.filter_by(country=country)

    # Filter on the data provider
    if provider:
        query = query.filter_by(provider=provider)

    if as_query:
        return query
    else:
        cities = query.all()
        return (city._asdict() for city in cities)

def get_stations(name=None, city=None, as_query=False):
    '''
    Filter and return a dictionary or query of stations.

    Args:
        name (str): A station name.
        city (str): A city name.
        as_query (bool): Return the query object or a generator.

    Returns:
        generator(dict) or query: The stations.
    '''
    # Restrict the returned fields
    query = models.Station.query.with_entities(
        models.Station.name,
        models.Station.latitude,
        models.Station.longitude,
        models.Station.altitude
    )

    # Filter on the station name
    if name:
        query = query.filter_by(name=name)

    # Filter on the belonging city
    if city:
        query = query.join(models.City).filter(models.City.name == city)

    if as_query:
        return query
    else:
        stations = query.all()
        return (station._asdict() for station in stations)


def get_updates(city=None):
    '''
    Return the latest update time for one or more cities.

    Args:
        city (str): The city name. `None` implies all the cities.

    Returns:
        generator(dict): The update for each specified city.

    Raises:
        CityNotFound: The city cannot be found.
    '''
    token = '*' if city is None else city

    # Get the information on all the geojson files
    geojson_files = glob.glob('{0}/{1}.geojson'.format(
        app.config['GEOJSON_FOLDER'],
        token
    ))
    if len(geojson_files) == 0:
        raise CityNotFound("'{}' not found".format(city))

    # Get the edit time of each geojson file
    results = (
        {
            'city': geojson.split('/')[-1].split('.')[0],
            'update': os.path.getmtime(geojson)
        }
        for geojson in geojson_files
    )
    return results


def make_forecast(city, station, kind, timestamp):
    '''
    Forecast the number of bikes/spaces for a station at a certain time.

    Args:
        city (str): The name of the city the station belongs to.
        station (str): The station name.
        kind (str): Either "bikes" or "spaces"
        timestamp (float): The time at which the forecast should be made.

    Returns:
        dict: The forecast including the expected error.

    Raises:
        PastTimestamp: The `timestamp` argument is in the past.
        InvalidKind: The `kind` argument is not equal to "bikes" nor to "spaces".
        CityNotFound: The city cannot be found.
        StationNotFound: The station cannot be found.
        CityInactive: The city is inactive.
        CityUnpredicable: Predictions cannot be made for the city.
    '''
    # Timestamp is in the past
    if timestamp < dt.datetime.now().timestamp():
        raise PastTimestamp("'{}' is in the past".format(timestamp))

    # Kind is invalid
    if kind not in ('bikes', 'spaces'):
        raise InvalidKind("'{}' is not a valid kind")
    query = models.Station.query.join(models.City).filter(models.City.name == city)

    # City doesn't exist
    if query.count() == 0:
        raise CityNotFound("'{}' not found".format(city))
    query = query.filter(models.Station.name == station)

    # Station doesn't exist
    if query.count() == 0:
        raise StationNotFound("'{}' not found".format(station))

    # Run the query
    station = query.first()

    # City not active
    if not station.city.active:
        raise CityInactive("'{}' is inactive".format(city))

    # City not predictable
    if not station.city.predictable:
        raise CityUnpredicable("'{}' is unpredictable".format(city))

    # Build a forecast
    moment = dt.datetime.fromtimestamp(timestamp)
    forecast = {
        'city': city,
        'station': station.name,
        'kind': kind,
        'timestamp': timestamp,
        'moment': moment.isoformat(),
        'error': station.training.error
    }

    # Make a prediction for the station
    if kind == 'bikes':
        forecast['quantity'] = station.predict('bikes', moment)
    else:
        forecast['quantity'] = station.predict('spaces', moment)
    return forecast


def filter_stations(city, lat, lon, limit, kind=None, mode=None,
                    timestamp=None, quantity=None, confidence=None):
    '''
    Find suitable stations based on a starting point in a particular city.
    It's possible to filter by distance or/and by number of bikes/spaces.
    The parameters `kind`, `timestamp`, `quantity` and `confidence` are linked;
    if one of them is given then the others have to be also in order to be able
    to make forecasts.

    Args:
        city (str): The city in which to search for stations
        lat (float): The latitude of the center point.
        lon (float): The longitude of the center point.
        limit (int): The maximal number of returned stations.
        kind (str): Whether to forecast "bikes" or "spaces".
        mode (str): The travel mode (driving, walking, bicycling,
            transit).
        timestamp (float): The UNIX timestamp indicating the departure
            from the point of origin.
        quantity (int): The minimum number of bikes/spaces the station should have.
        confidence (float): The confidence level of the quantity prediction.

    Returns:
        List(dict): The stations, ordered by distance but not by confidence.

    Raises:
        PastTimestamp: The provided timestamp is in the past.
        ValueError: The first 4 arguments cannot be None. The limit has to be a
            positive integer. The mode has to be either driving, walking,
            bicycling or transit.
        CityNotFound: The city cannot be found.
    '''
    # Verify the timestamp is not in the past
    if timestamp is not None and timestamp < dt.datetime.now().timestamp():
        raise PastTimestamp("'{}' is in the past".format(timestamp))

    # Verify necessary arguments are not None
    for arg in (city, lat, lon, limit):
        if arg is None:
            raise ValueError("'{}' cannot be nil".format(arg))

    # Verify limit is not negative
    if not isinstance(limit, int) or limit < 0:
        raise ValueError("'limit' has to be a non-negative integer")

    # Verify mode is valid
    if mode is not None and mode not in ('driving', 'walking', 'bicycling', 'transit'):
        raise ValueError("'mode' has to be either 'driving', 'walking'" + \
                         "'bicycling' or 'transit'")

    # Verify confidence is valid
    if confidence is not None and not 0 <= confidence <= 1:
        raise ValueError("'confidence' should be a number between 0 and 1")

    # Query all the stations in the given city
    point = 'POINT({lat} {lon})'.format(lat=lat, lon=lon)
    query = get_stations(city=city, as_query=True)
    query = query.order_by(models.Station.position.distance_box(point))
    if query.count() == 0:
        raise CityNotFound("'{}' not found".format(city))

    # Filter by number of bikes/spaces and limit
    candidates = []
    if kind and mode and timestamp and quantity and confidence:
        origin = {'latitude': lat, 'longitude': lon}
        # Go through the stations in chunks
        chunk = query.paginate(per_page=5)
        while len(candidates) < limit and chunk.has_next is True:
            destinations = [station._asdict() for station in chunk.items]
            distances = google.distances(origin, destinations, mode, timestamp)
            # Forecast the number of bikes/spaces
            for station, distance in zip(destinations, distances):
                # Calculate estimated time of arrival
                eta = timestamp + distance
                forecasted = make_forecast(city, station['name'], kind, eta)
                # Check if the worst case scenario is acceptable
                worst_case = forecasted['quantity'] - norm.ppf(confidence) * forecasted['error']
                if worst_case >= quantity:
                    # Add the forecast to the station
                    station['forecast'] = forecasted
                    candidates.append(station)
                    # Stop if there are enough candidates
                    if len(candidates) >= limit:
                        break
            chunk = chunk.next()
    else:
        candidates = [station._asdict() for station in query.limit(limit)]
    # Return each station as a dictionary
    return candidates


def find_closest_city(lat, lon, as_object=False):
    '''
    Find the closest point to a given latitude and longitude.

    Args:
        lat (float): The latitude of the center point.
        lon (float): The longitude of the center point.
        as_object (boolean): Return the city as a models.City object, if not a dict.

    Returns:
        dict or query: The closest city.
    '''
    point = 'POINT({lat} {lon})'.format(lat=lat, lon=lon)
    query = models.City.query.with_entities(
        models.City.name,
        models.City.latitude,
        models.City.longitude,
        models.City.predictable,
        models.City.active,
        models.City.country,
        models.City.provider
    )
    city = query.order_by(models.City.position.distance_box(point)).first()
    if as_object:
        return city
    else:
        return city._asdict()
