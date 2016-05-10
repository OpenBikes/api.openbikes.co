import requests

from collecting import util


def stations(city):
    # The city parameter is necessary so that everything works
    response = requests.get('http://dynamisch.citybikewien.at/citybike_xml.php')
    data = util.load_xml(response.content)
    return normalize(data)


def normalize(stations):
    extract = util.extract_element
    normalized = lambda station: {
        'name': extract(station, 'name'),
        'address': extract(station, 'description'),
        'latitude': float(extract(station, 'latitude')),
        'longitude': float(extract(station, 'longitude')),
        'status': 'OPEN' if extract(station, 'status') == 'aktiv' else 'CLOSED',
        'bikes': int(extract(station, 'free_bikes')),
        'stands': int(extract(station, 'free_boxes'))
    }
    return [
        normalized(station)
        for station in stations.find_all('station')
    ]
