from flask import Blueprint, jsonify, request

from app import services as srv
from app.exceptions import (
    CityNotFound,
    CityInactive,
    CityUnpredicable,
    StationNotFound,
    PastTimestamp,
    InvalidKind
)


API_BP = Blueprint('apibp', __name__, url_prefix='/api')


@API_BP.route('/geojson/<string:city>', methods=['GET'])
def api_geojson(city):
    ''' Return the latest geojson file of a city. '''
    try:
        response = srv.geojson(city)
        response['status'] = 'success'
        return jsonify(response), 200
    except CityNotFound as exc:
        return jsonify({
            'status': 'failure',
            'message': str(exc)
        }), 404


@API_BP.route('/countries', methods=['GET'])
def api_countries():
    ''' Return the list of countries. '''
    args = request.args
    # Check arguments are valid
    for arg in args:
        if arg not in ('name', 'provider'):
            return jsonify({
                'status': 'failure',
                'message': "'{}' is not a valid parameter".format(arg)
            }), 400
    countries = list(srv.get_countries(
        name=args.get('name'),
        provider=args.get('provider')
    ))
    return jsonify({
        'status': 'success',
        'countries': countries,
        'count': len(countries)
    }), 200


@API_BP.route('/providers', methods=['GET'])
def api_providers():
    ''' Return the list of providers. '''
    args = request.args
    # Check arguments are valid
    for arg in args:
        if arg not in ('name', 'country'):
            return jsonify({
                'status': 'failure',
                'message': "'{}' is not a valid parameter".format(arg)
            }), 400
    providers = list(srv.get_providers(
        name=args.get('name'),
        country=args.get('country')
    ))
    return jsonify({
        'status': 'success',
        'countries': providers,
        'count': len(providers)
    }), 200


@API_BP.route('/cities', methods=['GET'])
def api_cities():
    ''' Return the list of cities. '''
    args = request.args
    # Check arguments are valid
    for arg in args:
        if arg not in ('name', 'country', 'provider', 'predictable', 'active'):
            return jsonify({
                'status': 'failure',
                'message': "'{}' is not a valid parameter".format(arg)
            }), 400
    cities = list(srv.get_cities(
        name=args.get('name'),
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
def api_stations():
    ''' Return the list of stations. '''
    args = request.args
    # Check arguments are valid
    for arg in args:
        if arg not in ('name', 'city'):
            return jsonify({
                'status': 'failure',
                'message': "'{}' is not a valid parameter".format(arg)
            }), 400
    stations = list(srv.get_stations(
        name=args.get('name'),
        city=args.get('city')
    ))
    return jsonify({
        'status': 'success',
        'stations': stations,
        'count': len(stations)
    }), 200


@API_BP.route('/updates', methods=['GET'])
def api_updates():
    ''' Return the list of latest updates for each city. '''
    args = request.args
    # Check arguments are valid
    for arg in args:
        if arg not in 'city':
            return jsonify({
                'status': 'failure',
                'message': "'{}' is not a valid parameter".format(arg)
            }), 400
    try:
        updates = list(srv.get_updates(args.get('city')))
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


@API_BP.route('/forecast/<string:city>/<string:station>/<string:kind>/<float:timestamp>', methods=['GET'])
def api_forecast(city, station, kind, timestamp):
    ''' Return a forecast for a station at a given time. '''
    error = lambda e: {
        'status': 'failure',
        'message': str(e)
    }
    try:
        response = srv.make_forecast(city, station, kind, timestamp)
        response['status'] = 'success'
        return jsonify(response), 200
    except (PastTimestamp, InvalidKind, CityNotFound, StationNotFound,
            CityInactive, CityUnpredicable) as exc:
        return jsonify(error(exc)), 404


@API_BP.route('/filter_stations', methods=['GET'])
def api_filter_stations():
    ''' Return filtered stations. '''
    error = lambda e: {
        'status': 'failure',
        'message': str(e)
    }
    # Check arguments are valid
    args = request.args
    for arg in args:
        if arg not in ('city', 'latitude', 'longitude', 'limit', 'kind',
                       'mode', 'timestamp', 'quantity'):
            return jsonify({
                'status': 'failure',
                'message': "'{}' is not a valid parameter".format(arg)
            }), 400
    try:
        stations = srv.filter_stations(
            city=args.get('city'),
            lat=float(args['latitude']) if args.get('latitude') else None,
            lon=float(args['longitude']) if args.get('longitude') else None,
            limit=int(args['limit']) if args.get('limit') else None,
            kind=args.get('kind'),
            mode=args.get('mode'),
            timestamp=float(args['timestamp']) if args.get('timestamp') else None,
            quantity=int(args['quantity']) if args.get('quantity') else None,
            confidence=0.95,
        )
        return jsonify({
            'status': 'success',
            'stations': stations
        })
    except (PastTimestamp, InvalidKind, CityNotFound, CityInactive,
            CityUnpredicable, ValueError) as exc:
        return jsonify(error(exc)), 404
