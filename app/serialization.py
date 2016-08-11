def serialize_city(city):
    return {
        'active': city.active,
        'country': city.country,
        'latitude': city.latitude,
        'longitude': city.longitude,
        'name': city.name,
        'predictable': city.predictable,
        'provider': city.provider,
        'slug': city.slug
    }


def serialize_station(station):
    return {
        'altitude': station.altitude,
        'docks': station.docks,
        'latitude': station.latitude,
        'longitude': station.longitude,
        'name': station.name,
        'slug': station.slug,
    }
