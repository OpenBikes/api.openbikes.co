import datetime as dt

from app import app
from app import models
from app.database import session


client = app.test_client()


def test_api_geojson_valid_city():
    ''' Check api_geojson handles a valid city. '''
    rv = client.get('/api/geojson/Toulouse')
    assert rv.status_code == 200


def test_api_geojson_invalid_city():
    ''' Check api_geojson handles an invalid city. '''
    rv = client.get('/api/geojson/xyz')
    assert rv.status_code == 404


def test_api_cities_invalid_parameter():
    ''' Check api_cities doesn't accept invalid parameters. '''
    rv = client.get('/api/cities', query_string='foo=bar')
    assert rv.status_code == 400


def test_api_cities_valid_parameters():
    ''' Check api_cities handles all valid parameters. '''
    query = 'name=Toulouse&predictable=1&active=1&country=France&provider=jcdecaux'
    rv = client.get('/api/cities', query_string=query)
    assert rv.status_code == 200


def test_api_stations_invalid_parameter():
    ''' Check api_stations doesn't accept invalid parameters. '''
    rv = client.get('/api/stations', query_string='foo=bar')
    assert rv.status_code == 400


def test_api_stations_valid_parameters():
    ''' Check api_stations handles all valid parameters. '''
    query = 'name=00003 - POMME&city=Toulouse'
    rv = client.get('/api/stations', query_string=query)
    assert rv.status_code == 200


def test_api_updates_invalid_parameter():
    ''' Check api_updates doesn't accept invalid parameters. '''
    rv = client.get('/api/updates', query_string='foo=bar')
    assert rv.status_code == 400


def test_api_updates_all():
    ''' Check api_updates works with no parameters. '''
    rv = client.get('/api/updates')
    assert rv.status_code == 200


def test_api_updates_invalid_city():
    ''' Check api_updates handles invalid city. '''
    rv = client.get('/api/updates', query_string='city=xyz')
    assert rv.status_code == 404


def test_api_updates_valid_city():
    ''' Check api_updates handles valid city. '''
    rv = client.get('/api/updates', query_string='city=Toulouse')
    assert rv.status_code == 200


def test_api_forecast_invalid_city():
    ''' Check api_forecast handles invalid city. '''
    rv = client.get('/api/forecast/{city}/{station}/{kind}/{timestamp}'.format(
        city='xyz',
        station='00003 - POMME',
        kind='bikes',
        timestamp=(dt.datetime.now() + dt.timedelta(minutes=1)).timestamp()
    ))
    assert rv.status_code == 404


def test_api_forecast_invalid_station():
    ''' Check api_forecast handles invalid station. '''
    rv = client.get('/api/forecast/{city}/{station}/{kind}/{timestamp}'.format(
        city='Toulouse',
        station='xyz',
        kind='bikes',
        timestamp=(dt.datetime.now() + dt.timedelta(minutes=1)).timestamp()
    ))
    assert rv.status_code == 404


def test_api_forecast_invalid_kind():
    ''' Check api_forecast handles invalid kind. '''
    rv = client.get('/api/forecast/{city}/{station}/{kind}/{timestamp}'.format(
        city='Toulouse',
        station='00003 - POMME',
        kind='xyz',
        timestamp=(dt.datetime.now() + dt.timedelta(minutes=1)).timestamp()
    ))
    assert rv.status_code == 404


def test_api_forecast_invalid_timestamp():
    ''' Check api_forecast handles invalid timestamp. '''
    rv = client.get('/api/forecast/{city}/{station}/{kind}/{timestamp}'.format(
        city='Toulouse',
        station='00003 - POMME',
        kind='bikes',
        # Timestamp in the past
        timestamp=(dt.datetime.now() - dt.timedelta(minutes=1)).timestamp()
    ))
    assert rv.status_code == 404


def test_api_forecast_city_disabled():
    ''' Check api_forecast handles disabled city. '''
    # Setup
    city = models.City.query.filter_by(name='Toulouse').first()
    city.active = False
    session.commit()
    # Test
    rv = client.get('/api/forecast/{city}/{station}/{kind}/{timestamp}'.format(
        city='Toulouse',
        station='00003 - POMME',
        kind='bikes',
        timestamp=(dt.datetime.now() + dt.timedelta(minutes=1)).timestamp()
    ))
    assert rv.status_code == 404
    # Tear down
    city = models.City.query.filter_by(name='Toulouse').first()
    city.active = True
    session.commit()


def test_api_forecast_city_unpredicable():
    ''' Check api_forecast handles unpredicable city. '''
    # Setup
    city = models.City.query.filter_by(name='Toulouse').first()
    city.predictable = False
    session.commit()
    # Test
    rv = client.get('/api/forecast/{city}/{station}/{kind}/{timestamp}'.format(
        city='Toulouse',
        station='00003 - POMME',
        kind='bikes',
        timestamp=(dt.datetime.now() + dt.timedelta(minutes=1)).timestamp()
    ))
    assert rv.status_code == 404
    # Tear down
    city = models.City.query.filter_by(name='Toulouse').first()
    city.predictable = True
    session.commit()


def test_api_forecast_bikes():
    ''' Check api_forecast forecast bikes. '''
    rv = client.get('/api/forecast/{city}/{station}/{kind}/{timestamp}'.format(
        city='Toulouse',
        station='00003 - POMME',
        kind='bikes',
        timestamp=(dt.datetime.now() + dt.timedelta(minutes=1)).timestamp()
    ))
    assert rv.status_code == 200


def test_api_forecast_spaces():
    ''' Check api_forecast forecast spaces. '''
    rv = client.get('/api/forecast/{city}/{station}/{kind}/{timestamp}'.format(
        city='Toulouse',
        station='00003 - POMME',
        kind='spaces',
        timestamp=(dt.datetime.now() + dt.timedelta(minutes=1)).timestamp()
    ))
    assert rv.status_code == 200


def test_api_filter_invalid_parameter():
    ''' Check api_filter doesn't accept invalid parameters. '''
    rv = client.get('/api/filter', query_string='foo=bar')
    assert rv.status_code == 400


def test_api_filter_without_prediction():
    ''' Check api_filter works without predictions. '''
    query = 'city=Toulouse&latitude=43.6&longitude=1.4333&limit=1'
    rv = client.get('/api/filter', query_string=query)
    assert rv.status_code == 200


def test_api_filter_with_prediction():
    ''' Check api_filter works with predictions. '''
    query = 'city=Toulouse&latitude=43.6&longitude=1.4333&limit=1' + \
            '&kind=bikes&mode=walking&quantity=1&timestamp={timestamp}'.format(
                timestamp=(dt.datetime.now() + dt.timedelta(minutes=1)).timestamp()
            )
    rv = client.get('/api/filter', query_string=query)
    assert rv.status_code == 200


def test_api_filter_invalid_city():
    ''' Check api_filter handles invalid city names. '''
    query = 'city=xyz&latitude=43.6&longitude=1.4333&limit=1'
    rv = client.get('/api/filter', query_string=query)
    assert rv.status_code == 404


def test_api_filter_invalid_timestamp():
    ''' Check api_filter handles invalid timestamp. '''
    query = 'city=Toulouse&latitude=43.6&longitude=1.4333&limit=1' + \
            '&kind=bikes&mode=walking&quantity=1&timestamp={timestamp}'.format(
                timestamp=(dt.datetime.now() - dt.timedelta(minutes=1)).timestamp()
            )
    rv = client.get('/api/filter', query_string=query)
    assert rv.status_code == 404
