import datetime as dt

from flask import abort, Blueprint, jsonify, request
import voluptuous as vol

from app import services as srv
from app import voluptuous_util as vol_util
from app.exceptions import (
    CityNotFound,
    CityInactive,
    CityUnpredicable,
    InvalidKind,
    StationNotFound
)
from app.views import util


API_BP = Blueprint('apibp', __name__, url_prefix='')


@API_BP.route('/geojson/<string:city_slug>', methods=['GET'])
@util.crossdomain(origin='*')
def api_geojson(city_slug):
    ''' Return the latest geojson file of a city. '''
    try:
        geojson = srv.geojson(city_slug)
        return jsonify(geojson)
    except CityNotFound:
        abort(412)


@API_BP.route('/countries', methods=['GET'])
@util.crossdomain(origin='*')
def api_countries():
    ''' Return the list of countries. '''
    countries = list(srv.get_countries(provider=request.args.get('provider')))
    return jsonify(countries)


@API_BP.route('/providers', methods=['GET'])
@util.crossdomain(origin='*')
def api_providers():
    ''' Return the list of providers. '''
    providers = list(srv.get_providers(country=request.args.get('country')))
    return jsonify(providers)


@API_BP.route('/cities', methods=['GET'])
@util.crossdomain(origin='*')
def api_cities():
    ''' Return the list of cities. '''
    cities = list(srv.get_cities(
        slug=request.args.get('city_slug'),
        country=request.args.get('country'),
        provider=request.args.get('provider'),
        predictable=request.args.get('predictable'),
        active=request.args.get('active')
    ))
    return jsonify(cities)


@API_BP.route('/stations', methods=['GET'])
@util.crossdomain(origin='*')
def api_stations():
    ''' Return the list of stations. '''
    stations = list(srv.get_stations(
        city_slug=request.args.get('city_slug'),
        slug=request.args.get('station_slug')
    ))
    return jsonify(stations)


@API_BP.route('/updates', methods=['GET'])
@util.crossdomain(origin='*')
def api_updates():
    ''' Return the list of latest updates for each city. '''
    try:
        updates = list(srv.get_updates(request.args.get('city_slug')))
        for i, update in enumerate(updates):
            updates[i]['update'] = update['update'].isoformat()
        return jsonify(updates)
    except CityNotFound:
        abort(412)


@API_BP.route('/forecast', methods=['POST', 'REPORT'])
@util.crossdomain(origin='*')
def api_forecast():
    ''' Return a forecast for a station at a given time. '''
    schema = vol.Schema({
        'city_slug': str,
        'station_slug': str,
        'kind': vol.Any('bikes', 'spaces'),
        'moment': vol.All(vol.Coerce(float), vol_util.Timestamp())
    }, required=True)
    try:
        data = schema(request.get_json(force=True))
    except vol.MultipleInvalid:
        abort(400)
    try:
        response = srv.make_forecast(**data)
        return jsonify(response)
    except (InvalidKind, CityNotFound, StationNotFound, CityInactive, CityUnpredicable):
        abort(412)


@API_BP.route('/filtered_stations', methods=['POST', 'REPORT'])
@util.crossdomain(origin='*')
def api_filtered_stations():
    ''' Return filtered stations. '''
    schema = vol.Schema({
        vol.Required('city_slug'): str,
        vol.Required('limit'): vol.All(vol.Coerce(int), vol.Range(min=1)),
        vol.Required('latitude'): vol.Any(None, vol.All(vol.Coerce(float), vol.Range(min=-90, max=90))),
        vol.Required('longitude'): vol.Any(None, vol.All(vol.Coerce(float), vol.Range(min=0, max=180))),
        'kind': vol.Any('bikes', 'spaces'),
        'mode': vol.Any('walking', 'bicycling'),
        'moment': vol.All(vol.Coerce(float), vol_util.Timestamp()),
        'desired_quantity': vol.All(vol.Coerce(int), vol.Range(min=1)),
        'confidence': vol.All(vol.Coerce(float), vol.Range(min=0, max=1))
    })
    try:
        data = schema(request.get_json(force=True))
    except vol.MultipleInvalid:
        abort(400)
    try:
        return jsonify(list(srv.filter_stations(**data)))
    except (InvalidKind, CityNotFound, CityInactive, CityUnpredicable):
        abort(412)


@API_BP.route('/closest_city/<float:latitude>/<float:longitude>', methods=['GET'])
@util.crossdomain(origin='*')
def api_closest_city(latitude, longitude):
    ''' Return the closest city for a given latitude and longitude. '''
    response = srv.find_closest_city(latitude, longitude)
    return jsonify(response)


@API_BP.route('/closest_station/<float:latitude>/<float:longitude>', methods=['GET'])
@util.crossdomain(origin='*')
def api_closest_station(latitude, longitude):
    ''' Return the closest station for a given latitude and longitude. '''
    response = srv.find_closest_station(latitude, longitude, request.args.get('city_slug'))
    return jsonify(response)


@API_BP.route('/metrics', methods=['GET'])
@util.crossdomain(origin='*')
def api_metrics():
    ''' Returns latest metrics. '''
    nbr_providers, nbr_countries, nbr_cities, nbr_stations = srv.get_metrics()
    response = {
        'providers': nbr_providers,
        'countries': nbr_countries,
        'cities': nbr_cities,
        'stations': nbr_stations
    }
    return jsonify(response)
