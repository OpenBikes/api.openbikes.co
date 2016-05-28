import json
from urllib.request import urlopen

import variables


def add(stations, size=50):
    '''
    Use the Google Maps Elevation API to add altitudes to a dataframe.
    Because the API has a limitation this function batches the work into
    "packages" that are successively send to the API. The size parameter
    determines the size of the packages. The function starts by looping
    through the stations and increments a counter. Once the counter has
    reached the package size then it sends a request to the API and resets the
    counter. Once it has parsed all the stations it unwraps what the API
    send back into a list of dictionaries and sends it back.
    '''
    base = 'https://maps.googleapis.com/maps/api/elevation/json?'
    locations = ''
    packages = []
    counter = 1
    for station in stations:
        locations += '{},{}|'.format(station['lat'], station['lon'])
        counter += 1
        if size <= counter:
            locations += ';'
            counter = 1
    # Remove the last ; if there is one
    if locations.endswith(';'):
        locations = locations[:-1]
    for loc in locations.split(';'):
        url = base + 'locations={0}&key={1}'.format(loc[:-1], variables.GOOGLE_ELEVATION_API_KEY)
        with urlopen(url) as response:
            data = json.loads(response.read().decode())
        packages.append(data['results'])
    # Melt the packages into one list
    altitudes = []
    for package in packages:
        altitudes.extend(package)
    # Merge the stations and the altitudes
    for i, alt in enumerate(altitudes):
        stations[i].update(alt)
    return stations
