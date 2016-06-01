import json
import os
from urllib.request import urlopen


def chunkify(l, p):
    '''
    Convert a list into a list of smaller lists. Each chunk is of size
    p. There are thus ceil(len(l) / p). Only the last chunk's size
    differs from the others. The last chunk is of size p if
    mod(len(l), p) equals 0 else it equals mod(len(l), p).

    Args:
        l (List): The list.
        p (int): The size of each chunk.

    Returns:
        List(List): The chunks.

    Raises:
        ValueError: p has to be a positive integer.
    '''
    if type(p) != int or p <= 0:
        raise ValueError("'p' should be a positive integer.")
    return (l[i:i + p] for i in range(0, len(l), p))


def unchunkify(l):
    '''
    Flatten chunks into a single list.

    Args:
        l (List(List)): The list of chunks to flatten.

    Returns:
        List: The flatten list.
    '''
    return sum(l, [])


def googleify(points):
    '''
    Format the a list of points into a string in order to perform
    queries with the Google Maps API.

    Args:
        points (List(dict)): The list of points. Each point is a dictionary
            at least containing a `latitude` and a `longitude` field.

    Returns:
        str: The query string.
    '''
    return '|'.join((
        '{lat},{lon}'.format(lat=point['latitude'], lon=point['longitude'])
        for point in points
    ))


def altitudes(points, chunk_size=50):
    '''
    Use the Google Maps Elevation API to find the altitudes of a list of
    points. Because there is a limitation on the number of points per
    query, the query is performed in chunks. The results are flattened
    when all the queries are done. The results are sorted in the same
    order as the original list.

    Args:
        points (List(dict)): The list of points. Each point is a dictionary
            at least containing a `latitude` and a `longitude` field.
        chunk_size (int): The number of points to include in each query.

    Returns:
        List(dict): The result of the Google Maps Elevation API for
            each provided point.
    '''
    if len(points) == 0:
        return []
    # Chunkify the points to not hit the API threshold
    chunks = chunkify(points, chunk_size)
    # Concatenate each chunk into a query string
    locations = [googleify(points) for points in chunks]
    # Get the altitudes in chunks
    base = 'https://maps.googleapis.com/maps/api/elevation/json?'
    altitudes = []
    for loc in locations:
        url = base + 'locations={loc}&key={key}'.format(
            loc=loc,
            key=os.environ.get('GOOGLE_ELEVATION_API_KEY')
        )
        with urlopen(url) as response:
            data = json.loads(response.read().decode())
            altitudes.append(data['results'])
    return unchunkify(altitudes)


def distances(origin, destinations, mode, timestamp, chunk_size=20):
    '''
    Using the Google Distance Matrix API to calculate the distance in
    seconds from a point of origin to each point in a list of points
    at a certain and for a certain travel mode. The resulting list is
    sorted in the order as the provided destinations list.

    Args:
        origin (dict): The origin is a dictionary at least containing a
            `latitude` and a `longitude` field.
        destinations (List(dict)): The list of points. Each point is a
            dictionary at least containing a `latitude` and a `longitude`
            field.
        mode (str): The travel mode (driving, walking, bicycling,
            transit).
        timestamp (float): The UNIX timestamp indicating the departure
            from the point of origin.
        chunk_size (int): The number of points to include in each query.

    Returns:
        List (float): The duration in seconds to go from the point of
            origin to each point in the provided destinations list.
    '''
    origin = '{lat},{lon}'.format(
        lat=origin['latitude'], lon=origin['longitude'])
    # Chunkify the points to not hit the API threshold
    chunks = chunkify(destinations, chunk_size)
    # Concatenate each chunk into a query string
    destinations = [googleify(points) for points in chunks]
    # Get the altitudes in chunks
    base = 'https://maps.googleapis.com/maps/api/distancematrix/json?'
    distances = []
    for dest in destinations:
        url = base + 'mode={mode}&key={key}&origins={origin}&destinations={destinations}&time={time}'.format(
            mode=mode,
            key=os.environ.get('GOOGLE_DISTANCE_MATRIX_API_KEY'),
            origin=origin,
            destinations=dest,
            time=timestamp
        )
        with urlopen(url) as response:
            data = json.loads(response.read().decode())['rows'][0]['elements']
            distances.append([d['duration']['value'] for d in data])
    return unchunkify(distances)
