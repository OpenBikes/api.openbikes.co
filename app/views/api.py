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


apibp = Blueprint('apibp', __name__, url_prefix='/api')


@apibp.route('/geojson/<string:city>', methods=['GET'])
def api_geojson(city):
    ''' Return the latest geojson file of a city. '''
    try:
        response = srv.geojson(city)
        response['status'] = 'success'
        return jsonify(response), 200
    except CityNotFound as e:
        return jsonify({
            'status': 'failure',
            'message': str(e)
        }), 404


@apibp.route('/cities', methods=['GET'])
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
    cities = list(srv.cities(
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


@apibp.route('/stations', methods=['GET'])
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
    stations = list(srv.stations(
        name=args.get('name'),
        city=args.get('city')
    ))
    return jsonify({
        'status': 'success',
        'stations': stations,
        'count': len(stations)
    }), 200


@apibp.route('/updates', methods=['GET'])
def api_updates():
    ''' Return the list of latest updates for each city. '''
    args = request.args
    # Check arguments are valid
    for arg in args:
        if arg not in ('city'):
            return jsonify({
                'status': 'failure',
                'message': "'{}' is not a valid parameter".format(arg)
            }), 400
    try:
        updates = list(srv.updates(args.get('city')))
        return jsonify({
            'status': 'success',
            'updates': updates,
            'count': len(updates)
        })
    except CityNotFound as e:
        return jsonify({
            'status': 'failure',
            'message': str(e)
        }), 404


@apibp.route('/forecast/<string:city>/<string:station>/<string:kind>/<float:timestamp>', methods=['GET'])
def api_forecast(city, station, kind, timestamp):
    ''' Return a forecast for a station at a given time. '''
    error = lambda e: {
        'status': 'failure',
        'message': str(e)
    }
    try:
        response = srv.forecast(city, station, kind, timestamp)
        response['status'] = 'success'
        return jsonify(response), 200
    except PastTimestamp as e:
        return jsonify(error(e)), 404
    except InvalidKind as e:
        return jsonify(error(e)), 404
    except CityNotFound as e:
        return jsonify(error(e)), 404
    except StationNotFound as e:
        return jsonify(error(e)), 404
    except CityInactive as e:
        return jsonify(error(e)), 404
    except CityUnpredicable as e:
        return jsonify(error(e)), 404
    except Exception as e:
        return jsonify(error('Unknown error, please notify us')), 500


@apibp.route('/filter', methods=['GET'])
def api_filter():
    ''' Return filtered stations. '''
    error = lambda e: {
        'status': 'failure',
        'message': str(e)
    }
    # Check arguments are valid
    args = request.args
    for arg in args:
        if arg not in ('city', 'latitude', 'longitude', 'limit', 'kind',
                       'mode', 'timestamp', 'quantity', 'confidence'):
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
            confidence=float(args['confidence']) if args.get('confidence') else None,
        )
        return jsonify({
            'status': 'success',
            'stations': stations
        })
    except PastTimestamp as e:
        return jsonify(error(e)), 404
    except InvalidKind as e:
        return jsonify(error(e)), 404
    except CityNotFound as e:
        return jsonify(error(e)), 404
    except CityInactive as e:
        return jsonify(error(e)), 404
    except CityUnpredicable as e:
        return jsonify(error(e)), 404
    except ValueError as e:
        return jsonify(error(e)), 404
    except Exception as e:
        return jsonify(error(e)), 500

