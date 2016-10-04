'''
Example usage: `python station-clustering.py Toulouse`
'''

import argparse
import datetime as dt
import sys

# Update sys.path to access app folder
sys.path.append('..')

import pandas as pd

from app import services as srv


PARSER = argparse.ArgumentParser()
PARSER.add_argument('city', type=str, help='City for which to run the analysis')
PARAMS = PARSER.parse_args()

SINCE = dt.datetime(year=2015, month=10, day=1)
UNTIL = dt.datetime.now()

city = next(srv.get_cities(name=PARAMS.city, serialized=False))
stations = list(srv.get_stations(city_slug=city.slug, serialized=False))

fill_ratios = pd.DataFrame(
    index=(station.name for station in stations),
    columns=(i for i in range(24))
)
fill_ratios['latitude'] = [station.latitude for station in stations]
fill_ratios['longitude'] = [station.longitude for station in stations]
fill_ratios['altitude'] = [station.altitude for station in stations]

for station in stations:
    try:
        df = station.get_updates(SINCE, UNTIL)
        df['moment'] = df.index
        df['hour'] = df['moment'].apply(lambda x: x.hour)
        # Extract the time between each observation
        df['fill_ratio'] = df['bikes'] / (df['bikes'] + df['spaces'])
        for hour, group in df.groupby('hour'):
            fill_ratios[hour][station.name] = group['fill_ratio'].mean()
    except:
        pass

fill_ratios.dropna().to_csv('fill-ratios.csv')
