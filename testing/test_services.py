import datetime as dt
import types

from nose.tools import raises

from app import db
from app import services as srv
from app import models
from app.exceptions import (
    CityNotFound,
    CityInactive,
    CityUnpredicable,
    StationNotFound,
    InvalidKind
)


@raises(CityNotFound)
def test_srv_geojson_city_not_found():
    ''' Check geojson service raises exception with an invalid city. '''
    srv.geojson('xyz')


def test_srv_geojson_success():
    ''' Check geojson service works with a valid city. '''
    geojson = srv.geojson('toulouse')
    assert isinstance(geojson, dict)


def test_srv_get_countries_nil():
    ''' Check get_countries service returns nothing with an invalid parameter. '''
    countries = srv.get_countries(provider='xyz')
    assert isinstance(countries, types.GeneratorType)
    assert len(list(countries)) == 0


def test_srv_get_countries_all_params():
    ''' Check get_countries service works will all parameters. '''
    countries = srv.get_countries(provider='jcdecaux')
    assert isinstance(countries, types.GeneratorType)
    assert len(list(countries)) == 1


def test_srv_get_providers_nil():
    ''' Check get_providers service returns nothing with an invalid parameter. '''
    providers = srv.get_providers(country='xyz')
    assert isinstance(providers, types.GeneratorType)
    assert len(list(providers)) == 0


def test_srv_get_providers_all_params():
    ''' Check get_providers service works will all parameters. '''
    providers = srv.get_providers(country='France')
    assert isinstance(providers, types.GeneratorType)
    assert len(list(providers)) == 1


def test_srv_get_cities_nil():
    ''' Check get_cities service returns nothing with an invalid name. '''
    cities = srv.get_cities(name='xyz')
    assert isinstance(cities, types.GeneratorType)
    assert len(list(cities)) == 0


def test_srv_get_cities_all_params():
    ''' Check get_cities service works will all parameters. '''
    cities = srv.get_cities(name='Toulouse', slug='toulouse', country='France', provider='jcdecaux',
                            predictable=True, active=True)
    assert isinstance(cities, types.GeneratorType)
    assert len(list(cities)) == 1


def test_srv_get_stations_nil():
    ''' Check get_stations service returns nothing with an invalid name. '''
    stations = srv.get_stations(name='xyz')
    assert isinstance(stations, types.GeneratorType)
    assert len(list(stations)) == 0


def test_srv_get_stations_all_params():
    ''' Check get_stations service works will all parameters. '''
    stations = srv.get_stations(name='00003 - POMME', slug='00003-pomme', city_slug='toulouse')
    assert isinstance(stations, types.GeneratorType)
    assert len(list(stations)) == 1


def test_srv_updates_one_city():
    ''' Check get_updates service works for one city. '''
    updates = srv.get_updates(city_slug='toulouse')
    assert isinstance(updates, types.GeneratorType)
    assert len(list(updates)) == 1


def test_srv_get_updates_all_cities():
    ''' Check get_updates service works for all cities. '''
    updates = srv.get_updates(city_slug=None)
    assert isinstance(updates, types.GeneratorType)
    assert len(list(updates)) >= 1


@raises(InvalidKind)
def test_srv_make_forecast_invalid_kind():
    ''' Check make_forecast service raises exception on invalid kind. '''
    future = dt.datetime.now() + dt.timedelta(minutes=1)
    srv.make_forecast(city_slug='toulouse', station_slug='00003-pomme', kind='xyz', moment=future)


@raises(CityNotFound)
def test_srv_make_forecast_city_not_found():
    ''' Check make_forecast service raises exception on invalid city. '''
    future = dt.datetime.now() + dt.timedelta(minutes=1)
    srv.make_forecast(city_slug='xyz', station_slug='00003-pomme', kind='bikes', moment=future)


@raises(StationNotFound)
def test_srv_make_forecast_station_not_found():
    ''' Check make_forecast service raises exception on invalid station. '''
    future = dt.datetime.now() + dt.timedelta(minutes=1)
    srv.make_forecast(city_slug='toulouse', station_slug='xyz', kind='bikes', moment=future)


def test_srv_make_forecast_city_inactive():
    ''' Check make_forecast service raises exception on inactive city. '''
    session = db.session()
    # Setup
    city = models.City.query.filter_by(name='Toulouse').first()
    city.active = False
    session.commit()
    # Test
    @raises(CityInactive)
    def test():
        future = dt.datetime.now() + dt.timedelta(minutes=1)
        srv.make_forecast(
            city_slug='toulouse',
            station_slug='00003-pomme',
            kind='bikes',
            moment=future
        )
    # Tear down
    city = models.City.query.filter_by(name='Toulouse').first()
    city.active = True
    session.commit()


def test_srv_make_forecast_city_unpredictable():
    ''' Check make_forecast service raises exception on unpredictable city. '''
    session = db.session()
    # Setup
    city = models.City.query.filter_by(name='Toulouse').first()
    city.predictable = False
    session.commit()
    # Test
    @raises(CityUnpredicable)
    def test():
        future = dt.datetime.now() + dt.timedelta(minutes=1)
        srv.make_forecast(
            city_slug='toulouse',
            station_slug='00003-pomme',
            kind='bikes',
            moment=future
        )
    # Tear down
    city = models.City.query.filter_by(name='Toulouse').first()
    city.predictable = True
    session.commit()


def test_srv_make_forecast_bikes():
    ''' Check make_forecast service works for forecasting bikes. '''
    future = dt.datetime.now() + dt.timedelta(minutes=1)
    forecast = srv.make_forecast(
        city_slug='toulouse',
        station_slug='00003-pomme',
        kind='bikes',
        moment=future
    )
    assert isinstance(forecast, dict)
    assert len(forecast.keys()) > 0


def test_srv_forecast_spaces():
    ''' Check make_forecast service works for forecasting spaces. '''
    future = dt.datetime.now() + dt.timedelta(minutes=1)
    forecast = srv.make_forecast(
        city_slug='toulouse',
        station_slug='00003-pomme',
        kind='spaces',
        moment=future
    )
    assert isinstance(forecast, dict)
    assert len(forecast.keys()) > 0


@raises(ValueError)
def test_srv_filter_stations_invalid_limit_value():
    ''' Check filter_stations service raises exception on invalid limit value. '''
    srv.filter_stations(
        city_slug='toulouse',
        latitude=43.6,
        longitude=1.4333,
        limit=-1
    )


@raises(CityNotFound)
def test_srv_filter_stations_city_not_found():
    ''' Check filter_stations service raises exception on invalid city. '''
    srv.filter_stations(
        city_slug='xyz',
        latitude=43.6,
        longitude=1.4333,
        limit=1
    )


@raises(ValueError)
def test_srv_filter_stations_invalid_mode_value():
    ''' Check filter_stations service raises exception on invalid mode value. '''
    future = dt.datetime.now() + dt.timedelta(minutes=1)
    srv.filter_stations(
        city_slug='toulouse',
        latitude=43.6,
        longitude=1.4333,
        limit=1,
        kind='bikes',
        mode='xyz',
        moment=future,
        desired_quantity=1,
        confidence=0.5
    )


@raises(ValueError)
def test_srv_filter_stations_invalid_confidence_value():
    ''' Check filter_stations service raises exception on invalid confidence value. '''
    future = dt.datetime.now() + dt.timedelta(minutes=1)
    srv.filter_stations(
        city_slug='toulouse',
        latitude=43.6,
        longitude=1.4333,
        limit=1,
        kind='bikes',
        mode='walking',
        moment=future,
        desired_quantity=1,
        confidence=-1
    )


def test_srv_filter_stations_prediction():
    ''' Check filter_stations service works as expected with a prediction. '''
    future = dt.datetime.now() + dt.timedelta(minutes=1)
    stations = srv.filter_stations(
        city_slug='toulouse',
        latitude=43.6,
        longitude=1.4333,
        limit=1,
        kind='bikes',
        mode='walking',
        moment=future,
        desired_quantity=1,
        confidence=0.5
    )
    assert len(stations) == 1


def test_srv_find_closest_city():
    ''' Check find_closest_city service works. '''
    city = srv.find_closest_city(latitude=43.6, longitude=1.4333)
    assert city['name'] == 'Toulouse'


def test_srv_find_closest_station():
    ''' Check find_closest_station service works. '''
    station = srv.find_closest_station(latitude=43.6, longitude=1.4333)
    assert station['name'] == '00079 - PLACE LANGE'


def test_srv_get_metrics():
    ''' Check get_metrics service works. '''
    nbr_providers, nbr_countries, nbr_cities, nbr_stations = srv.get_metrics()
    assert isinstance(nbr_providers, int) and nbr_countries > 0
    assert isinstance(nbr_countries, int) and nbr_providers > 0
    assert isinstance(nbr_cities, int) and nbr_cities > 0
    assert isinstance(nbr_stations, int) and nbr_stations > 0
