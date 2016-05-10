import datetime as dt
import types

from nose.tools import raises

from app import services as srv
from app import models
from app.database import session
from app.exceptions import (
    CityNotFound,
    CityInactive,
    CityUnpredicable,
    StationNotFound,
    PastTimestamp,
    InvalidKind
)


@raises(CityNotFound)
def test_srv_geojson_city_not_found():
    ''' Check geojson service raises exception with an invalid city. '''
    srv.geojson('xyz')


def test_srv_geojson_success():
    ''' Check geojson service works with a valid city. '''
    geojson = srv.geojson('Toulouse')
    assert type(geojson) == dict


def test_srv_cities_nil():
    ''' Check cities service returns nothing with an invalid name. '''
    cities = srv.cities(name='xyz')
    assert isinstance(cities, types.GeneratorType)
    assert len(list(cities)) == 0


def test_srv_cities_all_params():
    ''' Check cities service works will all parameters. '''
    cities = srv.cities(name='Toulouse', country='France', provider='jcdecaux',
                        predictable=True, active=True)
    print(cities, type(cities))
    assert isinstance(cities, types.GeneratorType)
    assert len(list(cities)) == 1


def test_srv_stations_nil():
    ''' Check stations service returns nothing with an invalid name. '''
    stations = srv.stations(name='xyz')
    assert isinstance(stations, types.GeneratorType)
    assert len(list(stations)) == 0


def test_srv_stations_all_params():
    ''' Check stations service works will all parameters. '''
    stations = srv.stations(name='00003 - POMME', city='Toulouse')
    assert isinstance(stations, types.GeneratorType)
    assert len(list(stations)) == 1


@raises(CityNotFound)
def test_srv_updates_city_not_found():
    ''' Check updates service raises exception with an invalid city. '''
    srv.updates(city='xyz')


def test_srv_updates_one_city():
    ''' Check updates service works for one city. '''
    updates = srv.updates(city='Toulouse')
    assert isinstance(updates, types.GeneratorType)
    assert len(list(updates)) == 1


def test_srv_updates_all_cities():
    ''' Check updates service works for all cities. '''
    updates = srv.updates(city=None)
    assert isinstance(updates, types.GeneratorType)
    assert len(list(updates)) >= 1


@raises(PastTimestamp)
def test_srv_forecast_past_timestamp():
    ''' Check forecast service raises exception on past timestamp. '''
    past = (dt.datetime.now() - dt.timedelta(minutes=1)).timestamp()
    srv.forecast(city='Toulouse', station='00003 - POMME', kind='bikes',
                 timestamp=past)


@raises(InvalidKind)
def test_srv_forecast_invalid_kind():
    ''' Check forecast service raises exception on invalid kind. '''
    future = (dt.datetime.now() + dt.timedelta(minutes=1)).timestamp()
    srv.forecast(city='Toulouse', station='00003 - POMME', kind='xyz',
                 timestamp=future)


@raises(CityNotFound)
def test_srv_forecast_city_not_found():
    ''' Check forecast service raises exception on invalid city. '''
    future = (dt.datetime.now() + dt.timedelta(minutes=1)).timestamp()
    srv.forecast(city='xyz', station='00003 - POMME', kind='bikes',
                 timestamp=future)


@raises(StationNotFound)
def test_srv_forecast_station_not_found():
    ''' Check forecast service raises exception on invalid station. '''
    future = (dt.datetime.now() + dt.timedelta(minutes=1)).timestamp()
    srv.forecast(city='Toulouse', station='xyz', kind='bikes',
                 timestamp=future)


def test_srv_forecast_city_inactive():
    ''' Check forecast service raises exception on inactive city. '''
    # Setup
    city = models.City.query.filter_by(name='Toulouse').first()
    city.active = False
    session.commit()
    # Test
    @raises(CityInactive)
    def test():
        future = (dt.datetime.now() + dt.timedelta(minutes=1)).timestamp()
        srv.forecast(city='Toulouse', station='00003 - POMME', kind='bikes',
                     timestamp=future)
    # Tear down
    city = models.City.query.filter_by(name='Toulouse').first()
    city.active = True
    session.commit()


def test_srv_forecast_city_unpredictable():
    ''' Check forecast service raises exception on unpredictable city. '''
    # Setup
    city = models.City.query.filter_by(name='Toulouse').first()
    city.predictable = False
    session.commit()
    # Test
    @raises(CityUnpredicable)
    def test():
        future = (dt.datetime.now() + dt.timedelta(minutes=1)).timestamp()
        srv.forecast(city='Toulouse', station='00003 - POMME', kind='bikes',
                     timestamp=future)
    # Tear down
    city = models.City.query.filter_by(name='Toulouse').first()
    city.predictable = True
    session.commit()


def test_srv_forecast_bikes():
    ''' Check forecast service works for forecasting bikes. '''
    future = (dt.datetime.now() + dt.timedelta(minutes=1)).timestamp()
    forecast = srv.forecast(city='Toulouse', station='00003 - POMME',
                            kind='bikes', timestamp=future)
    assert type(forecast) == dict
    assert len(forecast.keys()) > 0


def test_srv_forecast_spaces():
    ''' Check forecast service works for forecasting spaces. '''
    future = (dt.datetime.now() + dt.timedelta(minutes=1)).timestamp()
    forecast = srv.forecast(city='Toulouse', station='00003 - POMME',
                            kind='spaces', timestamp=future)
    assert type(forecast) == dict
    assert len(forecast.keys()) > 0


@raises(ValueError)
def test_srv_filter_stations_city_not_none():
    ''' Check filter_stations service doesn't accept None for the city argument. '''
    srv.filter_stations(None, 43.6, 1.4333, 1)


@raises(ValueError)
def test_srv_filter_stations_lat_not_none():
    ''' Check filter_stations service doesn't accept None for the lat argument. '''
    srv.filter_stations('Toulouse', None, 1.4333, 1)


@raises(ValueError)
def test_srv_filter_stations_lon_not_none():
    ''' Check filter_stations service doesn't accept None for the lon argument. '''
    srv.filter_stations('Toulouse', 43.6, None, 1)


@raises(ValueError)
def test_srv_filter_stations_limit_not_none():
    ''' Check filter_stations service doesn't accept None for the limit argument. '''
    srv.filter_stations('Toulouse', 43.6, 1.4333, None)


@raises(ValueError)
def test_srv_filter_stations_invalid_limit_value():
    ''' Check filter_stations service raises exception on invalid limit value. '''
    srv.filter_stations('Toulouse', 43.6, 1.4333, -1)


@raises(CityNotFound)
def test_srv_filter_stations_city_not_found():
    ''' Check filter_stations service raises exception on invalid city. '''
    srv.filter_stations('xyz', 43.6, 1.4333, 1)


@raises(ValueError)
def test_srv_filter_stations_invalid_mode_value():
    ''' Check filter_stations service raises exception on invalid mode value. '''
    future = (dt.datetime.now() + dt.timedelta(minutes=1)).timestamp()
    srv.filter_stations('Toulouse', 43.6, 1.4333, 1, kind='bikes', mode='xyz',
                        timestamp=future, quantity=1, confidence=0.5)


@raises(PastTimestamp)
def test_srv_filter_stations_invalid_timestamp_value():
    past = (dt.datetime.now() - dt.timedelta(minutes=1)).timestamp()
    ''' Check filter_stations service raises exception on invalid mode value. '''
    srv.filter_stations('Toulouse', 43.6, 1.4333, 1, kind='bikes', mode='walking',
                        timestamp=past, quantity=1, confidence=0.5)


@raises(ValueError)
def test_srv_filter_stations_invalid_confidence_value():
    ''' Check filter_stations service raises exception on invalid confidence value. '''
    future = (dt.datetime.now() + dt.timedelta(minutes=1)).timestamp()
    srv.filter_stations('Toulouse', 43.6, 1.4333, 1, kind='bikes', mode='walking',
                        timestamp=future, quantity=1, confidence=-1)


def test_srv_filter_stations_prediction():
    ''' Check filter_stations service works as expected with a prediction. '''
    future = (dt.datetime.now() + dt.timedelta(minutes=1)).timestamp()
    stations = srv.filter_stations('Toulouse', 43.6, 1.4333, 1, kind='bikes',
                                   mode='walking', timestamp=future, quantity=1,
                                   confidence=0.5,)
    assert len(stations) == 1
