from datetime import datetime

import requests

from collecting import util


def stations(city):
    # The city parameter is necessary so that everything works
    response = requests.get('http://minaport.ubweb.jp/stations.php')
    data = util.load_xml(response.content)
    return normalize(data)


def normalize(stations):
    extract = util.extract_attribute
    normalized = lambda station: {
        'name': extract(station, 'stname'),
        'address': extract(station, 'staddr'),
        'latitude': float(extract(station, 'stlat')),
        'longitude': float(extract(station, 'stlng')),
        'status': 'CLOSED' if extract(station, 'stat1') == '0'
                  and extract(station, 'stat2') == '0' else 'OPEN',
        'bikes': int(extract(station, 'stat1')),
        'stands': int(extract(station, 'stat2')),
        'update': datetime.strptime(extract(station, 'date'),
                                    '%Y-%m-%d %H:%M:%S').isoformat()
    }
    return [
        normalized(station)
        for station in stations.find_all('marker')
    ]
