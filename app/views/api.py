from flask import Blueprint, jsonify, request

from app import services as srv
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
        geojson, update = srv.geojson(city_slug)
        try:
            geojson['update'] = update.isoformat()
            geojson['status'] = 'success'
        except TypeError:
            pass
        return jsonify(geojson), 200
    except CityNotFound as exc:
        return jsonify({
            'status': 'failure',
            'message': str(exc)
        }), 404


@API_BP.route('/countries', methods=['GET'])
@util.crossdomain(origin='*')
def api_countries():
    ''' Return the list of countries. '''
    args = request.args
    # Check arguments are valid
    for arg in args:
        if arg not in ('provider',):
            return jsonify({
                'status': 'failure',
                'message': "'{}' is not a valid parameter".format(arg)
            }), 400
    countries = list(srv.get_countries(
        provider=args.get('provider')
    ))
    return jsonify({
        'status': 'success',
        'countries': countries,
        'count': len(countries)
    }), 200


@API_BP.route('/providers', methods=['GET'])
@util.crossdomain(origin='*')
def api_providers():
    ''' Return the list of providers. '''
    args = request.args
    # Check arguments are valid
    for arg in args:
        if arg not in ('country',):
            return jsonify({
                'status': 'failure',
                'message': "'{}' is not a valid parameter".format(arg)
            }), 400
    providers = list(srv.get_providers(
        country=args.get('country')
    ))
    return jsonify({
        'status': 'success',
        'providers': providers,
        'count': len(providers)
    }), 200


@API_BP.route('/cities', methods=['GET'])
@util.crossdomain(origin='*')
def api_cities():
    ''' Return the list of cities. '''
    args = request.args
    # Check arguments are valid
    for arg in args:
        if arg not in ('city_slug', 'country', 'provider', 'predictable', 'active'):
            return jsonify({
                'status': 'failure',
                'message': "'{}' is not a valid parameter".format(arg)
            }), 400
    cities = list(srv.get_cities(
        slug=args.get('city_slug'),
        country=args.get('country'),
        provider=args.get('provider'),
        predictable=args.get('predictable'),
        active=args.get('active')
    ))
    return jsonify({
        'status': 'success',
        'cities': cities,
        'count': len(cities)
    }), 200


@API_BP.route('/stations', methods=['GET'])
@util.crossdomain(origin='*')
def api_stations():
    ''' Return the list of stations. '''
    args = request.args
    # Check arguments are valid
    for arg in args:
        if arg not in ('city_slug', 'station_slug'):
            return jsonify({
                'status': 'failure',
                'message': "'{}' is not a valid parameter".format(arg)
            }), 400
    stations = list(srv.get_stations(
        city_slug=args.get('city_slug'),
        slug=args.get('city_slug')
    ))
    return jsonify({
        'status': 'success',
        'stations': stations,
        'count': len(stations)
    }), 200


@API_BP.route('/updates', methods=['GET'])
@util.crossdomain(origin='*')
def api_updates():
    ''' Return the list of latest updates for each city. '''
    args = request.args
    # Check arguments are valid
    for arg in args:
        if arg not in ('city_slug',):
            return jsonify({
                'status': 'failure',
                'message': "'{}' is not a valid parameter".format(arg)
            }), 400
    try:
        updates = list(srv.get_updates(args.get('city_slug')))
        for i, update in enumerate(updates):
            updates[i]['update'] = update['update'].isoformat()

        return jsonify({
            'status': 'success',
            'updates': updates,
            'count': len(updates)
        })
    except CityNotFound as exc:
        return jsonify({
            'status': 'failure',
            'message': str(exc)
        }), 404


@API_BP.route('/forecast/<string:city_slug>/<string:station_slug>/<string:kind>/<float:timestamp>', methods=['GET'])
@util.crossdomain(origin='*')
def api_forecast(city_slug, station_slug, kind, timestamp):
    ''' Return a forecast for a station at a given time. '''
    error = lambda e: {
        'status': 'failure',
        'message': str(e)
    }
    try:
        response = srv.make_forecast(city_slug, station_slug, kind, timestamp)
        response['status'] = 'success'
        return jsonify(response), 200
    except (InvalidKind, CityNotFound, StationNotFound, CityInactive,
            CityUnpredicable) as exc:
        return jsonify(error(exc)), 404


@API_BP.route('/filtered_stations', methods=['GET'])
@util.crossdomain(origin='*')
def api_filtered_stations():
    ''' Return filtered stations. '''
    error = lambda e: {
        'status': 'failure',
        'message': str(e)
    }
    # Check arguments are valid
    args = request.args
    for arg in args:
        if arg not in ('city_slug', 'latitude', 'longitude', 'limit', 'kind', 'mode', 'timestamp',
                       'quantity'):
            return jsonify({
                'status': 'failure',
                'message': "'{}' is not a valid parameter".format(arg)
            }), 400
    try:
        stations = srv.filter_stations(
            city_slug=args.get('city_slug'),
            lat=float(args['latitude']) if args.get('latitude') else None,
            lon=float(args['longitude']) if args.get('longitude') else None,
            limit=int(args['limit']) if args.get('limit') else None,
            kind=args.get('kind'),
            mode=args.get('mode'),
            timestamp=float(args['timestamp']) if args.get(
                'timestamp') else None,
            quantity=int(args['quantity']) if args.get('quantity') else None,
            confidence=0.95,
        )
        return jsonify({
            'status': 'success',
            'stations': list(stations)
        })
    except (InvalidKind, CityNotFound, CityInactive, CityUnpredicable,
            ValueError) as exc:
        return jsonify(error(exc)), 404


@API_BP.route('/closest_city/<float:latitude>/<float:longitude>', methods=['GET'])
@util.crossdomain(origin='*')
def api_closest_city(latitude, longitude):
    ''' Return the closest city for a given latitude and longitude. '''
    response = srv.find_closest_city(latitude, longitude)
    response['status'] = 'success'
    return jsonify(response), 200


@API_BP.route('/closest_station/<float:latitude>/<float:longitude>', methods=['GET'])
@util.crossdomain(origin='*')
def api_closest_station(latitude, longitude):
    ''' Return the closest station for a given latitude and longitude. '''
    response = srv.find_closest_station(latitude, longitude)
    response['status'] = 'success'
    return jsonify(response), 200


@API_BP.route('/metrics', methods=['GET'])
@util.crossdomain(origin='*')
def api_metrics():
    ''' Returns latest metrics. '''
    nbr_providers, nbr_countries, nbr_cities, nbr_stations = srv.get_metrics()
    try:
        response = {
            'providers': nbr_providers,
            'countries': nbr_countries,
            'cities': nbr_cities,
            'stations': nbr_stations,
            'status': 'success'
        }
        return jsonify(response), 200
    except:
        return jsonify({'status': 'failure'}), 404
