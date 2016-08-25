import datetime as dt
import json

from app import app
from app import db
from app import models


CLIENT = app.test_CLIENT()


def test_api_geojson_valid_city():
    ''' Check api_geojson handles a valid city. '''
    response = CLIENT.get('/geojson/toulouse')
    assert response.status_code == 200


def test_api_geojson_invalid_city():
    ''' Check api_geojson handles an invalid city. '''
    response = CLIENT.get('/geojson/xyz')
    assert response.status_code == 412


def test_api_countries_valid_parameters():
    ''' Check api_countries handles all valid parameters. '''
    query = 'provider=jcdecaux'
    response = CLIENT.get('/countries', query_string=query)
    assert response.status_code == 200


def test_api_providers_valid_parameters():
    ''' Check api_providers handles all valid parameters. '''
    query = 'country=France'
    response = CLIENT.get('/providers', query_string=query)
    assert response.status_code == 200


def test_api_cities_valid_parameters():
    ''' Check api_cities handles all valid parameters. '''
    query = 'city_slug=toulouse&predictable=1&active=1&country=France&provider=jcdecaux'
    response = CLIENT.get('/cities', query_string=query)
    assert response.status_code == 200


def test_api_stations_valid_parameters():
    ''' Check api_stations handles all valid parameters. '''
    query = 'station_slug=00003-pomme&city_slug=toulouse'
    response = CLIENT.get('/stations', query_string=query)
    assert response.status_code == 200


def test_api_updates_all():
    ''' Check api_updates works with no parameters. '''
    response = CLIENT.get('/updates')
    assert response.status_code == 200


def test_api_updates_valid_city():
    ''' Check api_updates handles valid city. '''
    response = CLIENT.get('/updates', query_string='city_slug=toulouse')
    assert response.status_code == 200


def test_api_forecast_invalid_city():
    ''' Check api_forecast handles invalid city. '''
    payload = {
        'city_slug': 'xyz',
        'station_slug': '00003-pomme',
        'kind': 'bikes',
        'moment': (dt.datetime.now() + dt.timedelta(minutes=1)).timestamp()
    }
    response = CLIENT.post('/forecast', data=json.dumps(payload))
    assert response.status_code == 412


def test_api_forecast_invalid_station():
    ''' Check api_forecast handles invalid station. '''
    payload = {
        'city_slug': 'toulouse',
        'station_slug': 'xyz',
        'kind': 'bikes',
        'moment': (dt.datetime.now() + dt.timedelta(minutes=1)).timestamp()
    }
    response = CLIENT.post('/forecast', data=json.dumps(payload))
    assert response.status_code == 412


def test_api_forecast_invalid_kind():
    ''' Check api_forecast handles invalid kind. '''
    payload = {
        'city_slug': 'toulouse',
        'station_slug': '00003-pomme',
        'kind': 'xyz',
        'moment': (dt.datetime.now() + dt.timedelta(minutes=1)).timestamp()
    }
    response = CLIENT.post('/forecast', data=json.dumps(payload))
    assert response.status_code == 400


def test_api_forecast_city_disabled():
    ''' Check api_forecast handles disabled city. '''
    session = db.session()
    # Setup
    city = models.City.query.filter_by(name='Toulouse').first()
    city.active = False
    session.commit()
    # Test
    payload = {
        'city_slug': 'toulouse',
        'station_slug': '00003-pomme',
        'kind': 'bikes',
        'moment': (dt.datetime.now() + dt.timedelta(minutes=1)).timestamp()
    }
    response = CLIENT.post('/forecast', data=json.dumps(payload))
    assert response.status_code == 412
    # Tear down
    city = models.City.query.filter_by(name='Toulouse').first()
    city.active = True
    session.commit()


def test_api_forecast_city_unpredicable():
    ''' Check api_forecast handles unpredicable city. '''
    session = db.session()
    # Setup
    city = models.City.query.filter_by(name='Toulouse').first()
    city.predictable = False
    session.commit()
    # Test
    payload = {
        'city_slug': 'toulouse',
        'station_slug': '00003-pomme',
        'kind': 'bikes',
        'moment': (dt.datetime.now() + dt.timedelta(minutes=1)).timestamp()
    }
    response = CLIENT.post('/forecast', data=json.dumps(payload))
    assert response.status_code == 412
    # Tear down
    city = models.City.query.filter_by(name='Toulouse').first()
    city.predictable = True
    session.commit()


def test_api_forecast_bikes():
    ''' Check api_forecast can forecast bikes. '''
    payload = {
        'city_slug': 'toulouse',
        'station_slug': '00003-pomme',
        'kind': 'bikes',
        'moment': (dt.datetime.now() + dt.timedelta(minutes=1)).timestamp()
    }
    response = CLIENT.post('/forecast', data=json.dumps(payload))
    assert response.status_code == 200


def test_api_forecast_spaces():
    ''' Check api_forecast can forecast spaces. '''
    payload = {
        'city_slug': 'toulouse',
        'station_slug': '00003-pomme',
        'kind': 'spaces',
        'moment': (dt.datetime.now() + dt.timedelta(minutes=1)).timestamp()
    }
    response = CLIENT.post('/forecast', data=json.dumps(payload))
    assert response.status_code == 200


def test_api_filtered_without_forecasts():
    ''' Check api_filtered_stations works without forecasts. '''
    payload = {
        'city_slug': 'toulouse',
        'latitude': 43.6,
        'longitude': 1.4333,
        'limit': 1
    }
    response = CLIENT.post('/filtered_stations', data=json.dumps(payload))
    assert response.status_code == 200


def test_api_filtered_with_forecasts():
    ''' Check api_filtered_stations works with forecasts. '''
    payload = {
        'city_slug': 'toulouse',
        'latitude': 43.6,
        'longitude': 1.4333,
        'limit': 1,
        'kind': 'bikes',
        'mode': 'walking',
        'desired_quantity': 1,
        'moment': (dt.datetime.now() + dt.timedelta(minutes=1)).timestamp()
    }
    response = CLIENT.post('/filtered_stations', data=json.dumps(payload))
    assert response.status_code == 200


def test_api_filtered_invalid_city():
    ''' Check api_filtered_stations handles invalid city names. '''
    payload = {
        'city_slug': 'xyz',
        'latitude': 43.6,
        'longitude': 1.4333,
        'limit': 1
    }
    response = CLIENT.post('/filtered_stations', data=json.dumps(payload))
    assert response.status_code == 412


def test_api_closest_city():
    ''' Check api_closest_city works. '''
    response = CLIENT.get('/closest_city/{latitude}/{longitude}'.format(
        latitude='43.6',
        longitude='1.4333'
    ))
    assert response.status_code == 200


def test_api_closest_station():
    ''' Check api_closest_station works. '''
    response = CLIENT.get('/closest_station/{latitude}/{longitude}'.format(
        latitude='43.6',
        longitude='1.4333'
    ))
    assert response.status_code == 200


def test_api_closest_station_city_slug():
    ''' Check api_closest_station works with an initial city. '''
    response = CLIENT.get('/closest_station/{latitude}/{longitude}'.format(
        latitude='43.6',
        longitude='1.4333'
    ), query_string='city_slug=toulouse')
    assert response.status_code == 200
