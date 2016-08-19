import datetime as dt

from scipy.stats import norm

from app.exceptions import (
    CityNotFound,
    CityInactive,
    CityUnpredicable,
    InvalidKind,
    StationNotFound
)
from app import util
from app import models
from app.database import db_session_maker
from app.serialization import serialize_city, serialize_forecast, serialize_station
from collecting import google


def insert_stations(city, stations, altitudes):
    '''
    Insert stations and training schedules into the database.

    Args:
        city (models.City): A city identifier (the primary key in the database)
            which will be used as a foreign key to link the station to it's
            belonging city.
        stations (list of dicts): A list of dictionaries containing information
            relative to each station. The expected format is:
                {
                    'bikes': int,
                    'latitude': float,
                    'longitude': float,
                    'name': str,
                    'stands': int
                }
        altitudes (list of dicts): A list of dictionaries containing information
            relative to each station's altitude. The expected format is:
                {
                    'elevation': float
                }
    Returns:
        boolean: An indicator to make sure the insertions took place.
    '''
    session = db_session_maker()
    for station, altitude in zip(stations, altitudes):
        new_station = models.Station(
            altitude=altitude['elevation'],
            city_id=city.id,
            docks=station['bikes'] + station['stands'],
            latitude=altitude['location']['lat'],
            longitude=altitude['location']['lng'],
            name=station['name'],
            position='POINT({0} {1})'.format(altitude['location']['lat'],
                                             altitude['location']['lng']),
            slug=util.slugify(station['name'])
        )
        session.add(new_station)
        session.flush()
        session.add(models.Training(
            backward=7,
            error=99,
            forward=7,
            moment=dt.datetime.now(),
            station_id=new_station.id
        ))
    session.commit()
    return True


def geojson(city_slug):
    '''
    Open and return the latest geojson file of a city as a dictionary.

    Args:
        city_slug (str): The city's slugified name.

    Returns:
        dict: The latest geojson file.
        datetime: The time of most recent update.

    Raises:
        CityNotFound: The geojson file cannot be found.
    '''
    try:
        city = models.City.query.filter_by(slug=city_slug).first()
        return city.geojson, city.update
    except:
        raise CityNotFound("'{}' not found".format(city_slug))


def get_countries(provider=None):
    '''
    Filter and return a dictionary or query of countries.

    Args:
        provider (str): A data provider name.

    Returns:
        generator(dict) or query: The countries.
    '''
    # Restrict the returned fields
    query = models.City.query.distinct(models.City.country)

    # Filter on the data provider
    if provider:
        query = query.filter_by(provider=provider)

    return (city.country for city in query.all())


def get_providers(country=None):
    '''
    Filter and return a dictionary or query of providers.

    Args:
        country (str): A country name.

    Returns:
        generator(dict) or query: The providers.
    '''
    # Restrict the returned fields
    query = models.City.query.distinct(models.City.provider)

    # Filter on the country name
    if country:
        query = query.filter_by(country=country)

    return (city.provider for city in query.all())


def get_cities(name=None, slug=None, country=None, provider=None, predictable=False, active=False,
               as_query=False, serialized=True):
    '''
    Filter and return a dictionary or query of cities.

    Args:
        name (str): A city name.
        slug (str): The slugified city name.
        country (str): A country name.
        provider (str): A data provider name.
        predicable (bool): An indicator if the city is predicable or not.
        active (bool): An indicator if the city is active or not.
        as_query (bool): Return the query object or a generator.

    Returns:
        query or (dict): The cities.
    '''
    # Restrict the returned fields
    query = models.City.query

    # Filter on the city name
    if name:
        query = query.filter_by(name=name)

    # Filter on the slug
    if slug:
        query = query.filter_by(slug=slug)

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
        if serialized:
            return (serialize_city(city) for city in query)
        else:
            return (city for city in query)


def get_stations(name=None, slug=None, city_slug=None, as_query=False, serialized=True):
    '''
    Filter and return a dictionary or query of stations.

    Args:
        name (str): A station name.
        slug (str): A station's slugified name.
        city_slug (str): A city's slugified name.
        as_query (bool): Return the query object or a generator.

    Returns:
        query or (dict): The stations.
    '''
    # Restrict the returned fields
    query = models.Station.query

    # Filter on the station name
    if name:
        query = query.filter_by(name=name)

    # Filter on the slug
    if slug:
        query = query.filter_by(slug=slug)

    # Filter on the belonging city
    if city_slug:
        query = query.join(models.City).filter(models.City.slug == city_slug)

    if as_query:
        return query
    else:
        if serialized:
            return (serialize_station(station) for station in query)
        else:
            return (station for station in query)


def get_updates(city_slug=None, as_query=False):
    '''
    Return the latest update time for one or more cities.

    Args:
        city_slug (str): The city's slugified name. `None` implies all the cities.

    Returns:
        query or (dict): The update for each specified city.

    Raises:
        CityNotFound: The city cannot be found.
    '''
    query = models.City.query

    # Filter on the city slug
    if city_slug:
        query = query.filter_by(slug=city_slug)

    if as_query:
        return query
    else:
        return ({
            'name': city.name,
            'slug': city.slug,
            'update': city.update
        } for city in query.all())


def make_forecast(city_slug, station_slug, kind, moment, as_object=False):
    '''
    Forecast the number of bikes/spaces for a station at a certain time.

    Args:
        city_slug (str): The slugified name of the city the station belongs to.
        station_slug (str): The station's slugified name.
        kind (str): Either "bikes" or "spaces"
        moment (datetime.datetime): The time at which the forecast should be made for.

    Returns:
        models.Forecast or dict: The forecast including the expected error.

    Raises:
        InvalidKind: The `kind` argument is not equal to "bikes" nor to "spaces".
        CityNotFound: The city cannot be found.
        StationNotFound: The station cannot be found.
        CityInactive: The city is inactive.
        CityUnpredicable: Predictions cannot be made for the city.
    '''
    now = dt.datetime.now()

    # Kind is invalid
    if kind not in ('bikes', 'spaces'):
        raise InvalidKind("'{}' is not a valid kind")
    query = models.Station.query.join(models.City).filter(models.City.slug == city_slug)

    # City doesn't exist
    if query.count() == 0:
        raise CityNotFound("'{}' not found".format(city_slug))
    query = query.filter(models.Station.slug == station_slug)

    # Station doesn't exist
    if query.count() == 0:
        raise StationNotFound("'{}' not found".format(station_slug))

    # Run the query
    station = query.first()

    # City not active
    if not station.city.active:
        raise CityInactive("'{}' is inactive".format(city_slug))

    # City not predictable
    if not station.city.predictable:
        raise CityUnpredicable("'{}' is unpredictable".format(city_slug))

    # Make a prediction for the station
    if kind == 'bikes':
        prediction = station.predict('bikes', moment)
    else:
        prediction = station.predict('spaces', moment)

    forecast = models.Forecast(
        station=station,
        kind=kind,
        at=now,
        moment=moment,
        predicted=prediction,
        expected_error=station.training.error
    )
    session = db_session_maker()
    session.add(forecast)
    session.commit()

    if as_object:
        return forecast
    else:
        return serialize_forecast(forecast)


def filter_stations(city_slug, latitude, longitude, limit, kind=None, mode=None, moment=None,
                    desired_quantity=None, confidence=0.95):
    '''
    Find suitable stations based on a starting point in a particular city. It's possible to filter
    by distance or/and by number of bikes/spaces. The parameters `kind`, `moment`,
    `desired_quantity` and `confidence` are linked; if one of them is given then the others have to
    be also in order to be able to make forecasts.

    Args:
        city_slug (str): The city's slugified name in which to search for stations.
        latitude (float): The latitude of the center point.
        longitude (float): The longitude of the center point.
        limit (int): The maximal number of returned stations.
        kind (str): Whether to forecast "bikes" or "spaces".
        mode (str): The travel mode (driving, walking, bicycling or transit).
        moment (datetime.datetime): The UNIX timestamp indicating the departurefrom the point of
            origin.
        desired_quantity (int): The minimum number of bikes/spaces the station should have.
        confidence (float): The confidence level of the quantity prediction.

    Returns:
        (dict): The stations, ordered by distance but not by confidence.

    Raises:
        ValueError: The first 4 arguments cannot be None. The limit has to be a
            positive integer. The mode has to be either driving, walking,
            bicycling or transit.
        CityNotFound: The city cannot be found.
    '''

    # Verify limit is not below 1
    if not isinstance(limit, int) or limit < 1:
        raise ValueError("'limit' has to be higher or equal to 1")

    # Verify mode is valid
    if mode is not None and mode not in ('driving', 'walking', 'bicycling', 'transit'):
        raise ValueError("'mode' has to be either 'driving', 'walking', 'bicycling' or 'transit'")

    # Verify confidence is valid
    if confidence is not None and not 0 <= confidence <= 1:
        raise ValueError("'confidence' should be a number between 0 and 1")

    # Query all the stations in the given city
    point = 'POINT({latitude} {longitude})'.format(latitude=latitude, longitude=longitude)
    query = get_stations(city_slug=city_slug, as_query=True)
    query = query.order_by(models.Station.position.distance_box(point))

    if query.count() == 0:
        raise CityNotFound("'{}' not found".format(city_slug))

    # Filter by number of bikes/spaces and limit
    candidates = []
    if kind and mode and moment and desired_quantity and confidence:
        origin = {'latitude': latitude, 'longitude': longitude}
        # Go through the stations in chunks
        chunk = query.paginate(per_page=5)
        while len(candidates) < limit and chunk.has_next:
            destinations = [
                serialize_station(station)
                for station in chunk.items
                if station.has_regressor
            ]
            durations = google.fetch_durations(origin, destinations, mode, moment)
            # Forecast the number of bikes/spaces
            for station, duration in zip(destinations, durations):
                # Calculate estimated time of arrival
                eta = moment + dt.timedelta(seconds=duration)
                forecast = make_forecast(city_slug, station['slug'], kind, eta, as_object=True)
                # Check if the worst case scenario is acceptable
                worst_case = forecast.predicted - norm.ppf(confidence) * forecast.expected_error
                if worst_case >= desired_quantity:
                    # Add the forecast to the station
                    station['forecast'] = serialize_forecast(forecast)
                    candidates.append(station)
                    # Stop if there are enough candidates
                    if len(candidates) >= limit:
                        break
            chunk = chunk.next()
    else:
        candidates = (serialize_station(station) for station in query.limit(limit))
    # Return each station as a dictionary
    return candidates


def find_closest_city(latitude, longitude, as_object=False):
    '''
    Find the closest city to a given latitude and longitude.

    Args:
        latitude (float): The latitude of the center point.
        longitude (float): The longitude of the center point.
        as_object (boolean): Return the city as a models.City object,
            if not a dict.

    Returns:
         models.City or dict: The closest city.
    '''
    point = 'POINT({latitude} {longitude})'.format(latitude=latitude, longitude=longitude)
    query = models.City.query
    city = query.order_by(models.City.position.distance_box(point)).first()

    if as_object:
        return city
    else:
        return serialize_city(city)


def find_closest_station(latitude, longitude, city_slug=None, as_object=False):
    '''
    Find the closest station to a given latitude and longitude.

    Args:
        latitude (float): The latitude of the center point.
        longitude (float): The longitude of the center point.
        as_object (boolean): Return the station as a models.Station object,
            if not a dict.

    Returns:
        models.Station or dict: The closest station.
    '''
    point = 'POINT({latitude} {longitude})'.format(latitude=latitude, longitude=longitude)
    query = models.Station.query

    if city_slug:
        city = get_cities(slug=city_slug, as_query=True).first()
        query = query.filter_by(city=city)
    else:
        query = query.filter_by(city=find_closest_city(latitude, longitude, as_object=True))

    station = query.order_by(models.Station.position.distance_box(point)).first()

    if as_object:
        return station
    else:
        return serialize_station(station)


def get_metrics():
    '''
    Returns useful metrics.

    Returns:
        (int): The number of providers.
        (int): The number of countries.
        (int): The number of cities.
        (int): The number of stations.
    '''
    nbr_providers = sum(1 for _ in get_providers())
    nbr_countries = sum(1 for _ in get_countries())
    nbr_cities = sum(1 for _ in get_cities(serialized=False))
    nbr_stations = sum(1 for _ in get_stations(serialized=False))

    return nbr_providers, nbr_countries, nbr_cities, nbr_stations
