def convert_stations_to_geojson(stations: list) -> dict:
    return {
        'type': 'FeatureCollection',
        'features': [
            {
                'type': 'Feature',
                'geometry': {
                    'type': 'Point',
                    'coordinates': [
                        station.longitude,
                        station.latitude
                    ]
                },
                'properties': {
                    'name': station.name,
                    'altitude': station.altitude,
                    'is_available': station.is_available,
                    'city': getattr(getattr(station, 'city', None), 'name', None),
                    'country': getattr(getattr(getattr(station, 'city', None), 'country', None),
                                       'name', None),
                    'n_docks_taken': getattr(getattr(station, 'docks_update', None), 'n_taken',
                                             None),
                    'n_docks_empty': getattr(getattr(station, 'docks_update', None), 'n_empty',
                                             None),
                    'updated_at': getattr(getattr(station, 'docks_update', None), 'moment', None),
                },
            } for station in stations
        ]
    }
