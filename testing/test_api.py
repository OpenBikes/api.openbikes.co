import datetime as dt

from app import app
from app import models
from app.database import db_session


client = app.test_client()


def test_api_geojson_valid_city():
    ''' Check api_geojson handles a valid city. '''
    rv = client.get('/geojson/toulouse')
    assert rv.status_code == 200


def test_api_geojson_invalid_city():
    ''' Check api_geojson handles an invalid city. '''
    rv = client.get('/geojson/xyz')
    assert rv.status_code == 404


def test_api_countries_invalid_parameter():
    ''' Check api_countries doesn't accept invalid parameters. '''
    rv = client.get('/countries', query_string='foo=bar')
    assert rv.status_code == 400


def test_api_countries_valid_parameters():
    ''' Check api_countries handles all valid parameters. '''
    query = 'provider=jcdecaux'
    rv = client.get('/countries', query_string=query)
    assert rv.status_code == 200


def test_api_providers_valid_parameters():
    ''' Check api_providers handles all valid parameters. '''
    query = 'country=France'
    rv = client.get('/providers', query_string=query)
    assert rv.status_code == 200


def test_api_providers_invalid_parameter():
    ''' Check api_providers doesn't accept invalid parameters. '''
    rv = client.get('/providers', query_string='foo=bar')
    assert rv.status_code == 400


def test_api_cities_invalid_parameter():
    ''' Check api_cities doesn't accept invalid parameters. '''
    rv = client.get('/cities', query_string='foo=bar')
    assert rv.status_code == 400


def test_api_cities_valid_parameters():
    ''' Check api_cities handles all valid parameters. '''
    query = 'city_slug=toulouse&predictable=1&active=1&country=France&provider=jcdecaux'
    rv = client.get('/cities', query_string=query)
    assert rv.status_code == 200


def test_api_stations_invalid_parameter():
    ''' Check api_stations doesn't accept invalid parameters. '''
    rv = client.get('/stations', query_string='foo=bar')
    assert rv.status_code == 400


def test_api_stations_valid_parameters():
    ''' Check api_stations handles all valid parameters. '''
    query = 'station_slug=00003-pomme&city_slug=toulouse'
    rv = client.get('/stations', query_string=query)
    assert rv.status_code == 200


def test_api_updates_invalid_parameter():
    ''' Check api_updates doesn't accept invalid parameters. '''
    rv = client.get('/updates', query_string='foo=bar')
    assert rv.status_code == 400


def test_api_updates_all():
    ''' Check api_updates works with no parameters. '''
    rv = client.get('/updates')
    assert rv.status_code == 200


def test_api_updates_valid_city():
    ''' Check api_updates handles valid city. '''
    rv = client.get('/updates', query_string='city_slug=toulouse')
    assert rv.status_code == 200


def test_api_forecast_invalid_city():
    ''' Check api_forecast handles invalid city. '''
    rv = client.get('/forecast/{city_slug}/{station_slug}/{kind}/{timestamp}'.format(
        city_slug='xyz',
        station_slug='00003-pomme',
        kind='bikes',
        timestamp=(dt.datetime.now() + dt.timedelta(minutes=1)).timestamp()
    ))
    assert rv.status_code == 404


def test_api_forecast_invalid_station():
    ''' Check api_forecast handles invalid station. '''
    rv = client.get('/forecast/{city_slug}/{station_slug}/{kind}/{timestamp}'.format(
        city_slug='toulouse',
        station_slug='xyz',
        kind='bikes',
        timestamp=(dt.datetime.now() + dt.timedelta(minutes=1)).timestamp()
    ))
    assert rv.status_code == 404


def test_api_forecast_invalid_kind():
    ''' Check api_forecast handles invalid kind. '''
    rv = client.get('/forecast/{city_slug}/{station_slug}/{kind}/{timestamp}'.format(
        city_slug='toulouse',
        station_slug='00003-pomme',
        kind='xyz',
        timestamp=(dt.datetime.now() + dt.timedelta(minutes=1)).timestamp()
    ))
    assert rv.status_code == 404


def test_api_forecast_city_disabled():
    ''' Check api_forecast handles disabled city. '''
    # Setup
    city = models.City.query.filter_by(name='Toulouse').first()
    city.active = False
    db_session.commit()
    # Test
    rv = client.get('/forecast/{city_slug}/{station_slug}/{kind}/{timestamp}'.format(
        city_slug='toulouse',
        station_slug='00003-pomme',
        kind='bikes',
        timestamp=(dt.datetime.now() + dt.timedelta(minutes=1)).timestamp()
    ))
    assert rv.status_code == 404
    # Tear down
    city = models.City.query.filter_by(name='Toulouse').first()
    city.active = True
    db_session.commit()


def test_api_forecast_city_unpredicable():
    ''' Check api_forecast handles unpredicable city. '''
    # Setup
    city = models.City.query.filter_by(name='Toulouse').first()
    city.predictable = False
    db_session.commit()
    # Test
    rv = client.get('/forecast/{city_slug}/{station_slug}/{kind}/{timestamp}'.format(
        city_slug='toulouse',
        station_slug='00003-pomme',
        kind='bikes',
        timestamp=(dt.datetime.now() + dt.timedelta(minutes=1)).timestamp()
    ))
    assert rv.status_code == 404
    # Tear down
    city = models.City.query.filter_by(name='Toulouse').first()
    city.predictable = True
    db_session.commit()


def test_api_forecast_bikes():
    ''' Check api_forecast forecast bikes. '''
    rv = client.get('/forecast/{city_slug}/{station_slug}/{kind}/{timestamp}'.format(
        city_slug='toulouse',
        station_slug='00003-pomme',
        kind='bikes',
        timestamp=(dt.datetime.now() + dt.timedelta(minutes=1)).timestamp()
    ))
    assert rv.status_code == 200


def test_api_forecast_spaces():
    ''' Check api_forecast forecast spaces. '''
    rv = client.get('/forecast/{city_slug}/{station_slug}/{kind}/{timestamp}'.format(
        city_slug='toulouse',
        station_slug='00003-pomme',
        kind='spaces',
        timestamp=(dt.datetime.now() + dt.timedelta(minutes=1)).timestamp()
    ))
    assert rv.status_code == 200


def test_api_filtered_invalid_parameter():
    ''' Check api_filtered_stations doesn't accept invalid parameters. '''
    rv = client.get('/filtered_stations', query_string='foo=bar')
    assert rv.status_code == 400


def test_api_filtered_without_prediction():
    ''' Check api_filtered_stations works without predictions. '''
    query = 'city_slug=toulouse&latitude=43.6&longitude=1.4333&limit=1'
    rv = client.get('/filtered_stations', query_string=query)
    assert rv.status_code == 200


def test_api_filtered_with_prediction():
    ''' Check api_filtered_stations works with predictions. '''
    query = 'city_slug=toulouse&latitude=43.6&longitude=1.4333&limit=1' + \
            '&kind=bikes&mode=walking&quantity=1&timestamp={timestamp}'.format(
                timestamp=(dt.datetime.now() + dt.timedelta(minutes=1)).timestamp()
            )
    rv = client.get('/filtered_stations', query_string=query)
    assert rv.status_code == 200


def test_api_filtered_invalid_city():
    ''' Check api_filtered_stations handles invalid city names. '''
    query = 'city_slug=xyz&latitude=43.6&longitude=1.4333&limit=1'
    rv = client.get('/filtered_stations', query_string=query)
    assert rv.status_code == 404


def test_api_filtered_invalid_timestamp():
    ''' Check api_filtered_stations handles invalid timestamp. '''
    query = 'city_slug=toulouse&latitude=43.6&longitude=1.4333&limit=1' + \
            '&kind=bikes&mode=walking&quantity=1&timestamp={timestamp}'.format(
                timestamp=(dt.datetime.now() - dt.timedelta(minutes=1)).timestamp()
            )
    rv = client.get('/filter_stations', query_string=query)
    assert rv.status_code == 404


def test_api_closest_city():
    ''' Check api_closest_city works. '''
    rv = client.get('/closest_city/{latitude}/{longitude}'.format(
        latitude='43.6',
        longitude='1.4333'
    ))
    assert rv.status_code == 200


def test_api_closest_station():
    ''' Check api_closest_station works. '''
    rv = client.get('/closest_station/{latitude}/{longitude}'.format(
        latitude='43.6',
        longitude='1.4333'
    ))
    assert rv.status_code == 200
