import requests

from collecting import util


def stations(city):
    # The city parameter is necessary so that everything work
    payload = {
        'key': os.environ.get('LACUB_API_KEY'),
        'SERVICE': 'WFS',
        'VERSION': '1.1.0',
        'REQUEST': 'GetFeature',
        'TYPENAME': 'CI_VCUB_P',
        'SRSNAME': 'EPSG:4326'
    }
    response = requests.get('http://data.lacub.fr/wfs', params=payload)
    data = util.load_xml(response.content)
    return normalize(data)


def normalize(stations):
    extract = util.extract_element
    normalized = lambda station: {
        'name': extract(station, 'name'),
        'address': extract(station, 'name'),
        'latitude': float(extract(station, 'lat')),
        'longitude': float(extract(station, 'long')),
        'status': 'OPEN' if extract(station, 'locked') == 'false' else 'CLOSED',
        'bikes': int(extract(station, 'nbbikes')),
        'stands': int(extract(station, 'nbemptydocks')),
        'update': util.epoch_to_datetime(int(extract(station,
                                                     'latestupdatetime')),
                                         divisor=1000).isoformat()
    }
    return [
        normalized(station)
        for station in stations.find_all('station')
    ]
