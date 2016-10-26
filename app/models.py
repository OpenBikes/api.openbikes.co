import datetime as dt
import json

from geoalchemy2 import Geometry
import pandas as pd
from pandas.io.json import json_normalize
from sqlalchemy import (CheckConstraint, Column, Integer, String, Boolean, DateTime, Float,
                        ForeignKey, Text)
from sqlalchemy.orm import relationship

from app import db
from app import mongo_bikes_coll, mongo_weather_coll
from app import util
from training.util import check_regressor_exists, load_regressor
from training import munging


class City(db.Model):
    __tablename__ = 'cities'

    active = Column(Boolean, nullable=False, index=True)
    country = Column(String, nullable=False, index=True)
    _geojson = Column(Text, nullable=False)
    id = Column(Integer, primary_key=True, autoincrement=True)
    latitude = Column(Float, nullable=False, index=True)
    longitude = Column(Float, nullable=False, index=True)
    name = Column(String, nullable=False, index=True)
    name_api = Column(String, nullable=False, index=True)
    name_owm = Column(String, nullable=False, index=True)
    position = Column(Geometry('POINT'), nullable=False, index=True)
    predictable = Column(Boolean, nullable=False, index=True)
    provider = Column(String, nullable=False, index=True)
    slug = Column(String, nullable=False, index=True)
    update = Column(DateTime, nullable=False, index=True)

    stations = relationship('Station', back_populates='city', passive_deletes=True)

    def insert_station_updates(self, stations):

        collection = mongo_bikes_coll[self.name]

        for station in stations:
            name = station['name']
            timestamp = dt.datetime.strptime(station['update'], '%Y-%m-%dT%H:%M:%S')
            time = timestamp.time().isoformat()
            date = timestamp.date().isoformat()
            # Check the dates has already been inserted
            if collection.find({'_id': date}).count() == 0:
                collection.save({
                    '_id': date,
                    'u': []
                })
            # Add the station entry if it doesn't exist and there is data
            if collection.find({'_id': date, 'u.n': name}).count() == 0:
                collection.update({'_id': date, 'u.n': {'$nin': [name]}}, {
                    '$push': {
                        'u': {
                            'n': name,
                            'i': []
                        }
                    }
                })
            # Update the station with the new information
            if collection.find({'_id': date, 'u.n': name, 'u.i.m': time}).count() == 0:
                collection.update({'_id': date, 'u.n': name}, {
                    '$push': {
                        'u.$.i': {
                            'm': time,
                            'b': station['bikes'],
                            's': station['stands']
                        }
                    }
                })

    def insert_weather_update(self, weather_update):

        collection = mongo_weather_coll[self.name]

        # Extract the date
        date = weather_update['datetime'].date().isoformat()
        time = weather_update['datetime'].time().isoformat()
        # Check the dates has already been inserted
        if collection.find({'_id': date}).count() == 0:
            collection.save({
                '_id': date,
                'u': []
            })
        # Add the weather entry if it doesn't exist
        if collection.find({'_id': date, 'u.m': time}).count() == 0:
            # Update the day with the new information
            collection.update({'_id': date}, {
                '$push': {
                    'u': {
                        'm': time,
                        'd': weather_update['description'],
                        'p': weather_update['pressure'],
                        't': weather_update['temperature'],
                        'h': weather_update['humidity'],
                        'w': weather_update['wind_speed'],
                        'c': weather_update['clouds']
                    }
                }
            })

    def get_station_updates(self, since, until):

        collection = mongo_bikes_coll[self.name]

        cursor = collection.find({
            '_id': {
                '$gte': since.date().isoformat(),
                '$lte': until.date().isoformat()
            }
        })

        dfs = []

        for c in cursor:

            date = dt.datetime.strptime(c['_id'], '%Y-%m-%d')

            df = pd.concat((
                json_normalize(update, 'i', ['n'])
                for update in c['u']
            ))

            df['m'] = df['m'].apply(lambda x: dt.datetime.combine(
                date,
                dt.datetime.strptime(x, '%H:%M:%S').time())
            )

            dfs.append(df)

        updates_df = pd.concat(dfs)

        updates_df.rename(columns={
            'm': 'moment',
            'b': 'bikes',
            's': 'spaces',
            'n': 'station'
        }, inplace=True)

        updates_df.set_index('moment', inplace=True)
        updates_df.groupby(updates_df.index, sort=False).first()

        return updates_df

    def get_weather_updates(self, since, until):

        collection = mongo_weather_coll[self.name]

        cursor = collection.find({
            '_id': {
                '$gte': since.date().isoformat(),
                '$lte': until.date().isoformat()
            }
        })

        dfs = []

        for c in cursor:

            date = dt.datetime.strptime(c['_id'], '%Y-%m-%d')

            df = json_normalize(c, 'u', ['_id'])
            df['m'] = df['m'].apply(lambda x: dt.datetime.combine(
                date,
                dt.datetime.strptime(x, '%H:%M:%S').time())
            )
            dfs.append(df)

        weather_df = pd.concat(dfs)

        weather_df.rename(columns={
            'm': 'moment',
            'd': 'description',
            'p': 'pressure',
            'h': 'humidity',
            'w': 'wind',
            't': 'temperature',
            'c': 'clouds'
        }, inplace=True)

        weather_df.drop('_id', axis=1, inplace=True)
        weather_df.set_index('moment', inplace=True)
        weather_df.groupby(weather_df.index, sort=False).first()

        return weather_df

    @property
    def geojson(self):
        return json.loads(self._geojson)

    @geojson.setter
    def geojson(self, value):
        self._geojson = json.dumps(value)

    def __repr__(self):
        return '<City #{}>'.format(self.id)

    def __str__(self):
        return '<{}>'.format(self.name)


class Station(db.Model):
    __tablename__ = 'stations'

    altitude = Column(Float, nullable=False, index=True)
    id = Column(Integer, primary_key=True, autoincrement=True)
    docks = Column(Integer, CheckConstraint('0 <= docks'), nullable=False, index=True)
    latitude = Column(Float, nullable=False, index=True)
    longitude = Column(Float, nullable=False, index=True)
    name = Column(String, nullable=False, index=True)
    position = Column(Geometry('POINT'), nullable=False)
    slug = Column(String, nullable=False, index=True)

    city = relationship('City', back_populates='stations')
    city_id = Column(Integer, ForeignKey('cities.id', ondelete='CASCADE'), nullable=False, index=True)

    training = relationship('Training', uselist=False)

    forecasts = relationship('Forecast', back_populates='station', lazy='dynamic', passive_deletes=True)

    def get_updates(self, since, until):

        collection = mongo_bikes_coll[self.city.name]

        cursor = collection.find({
            '_id': {
                '$gte': since.date().isoformat(),
                '$lte': until.date().isoformat()
            },
            'u.n': self.name
        }, {
            'u': {
                '$elemMatch': {
                    'n': self.name
                }
            }
        })

        dfs = []

        for c in cursor:

            date = dt.datetime.strptime(c['_id'], '%Y-%m-%d')

            try:
                df = json_normalize(c['u'][0], 'i')
                df['m'] = df['m'].apply(lambda x: dt.datetime.combine(
                    date,
                    dt.datetime.strptime(x, '%H:%M:%S').time())
                )
            except KeyError: # No updates are available at a certain date yet the date exists
                continue

            # Refilter with pandas to take into account the time which is not indexed through Mongo
            df = df[(df['m'] >= since) & (df['m'] <= until)]

            dfs.append(df)

        updates_df = pd.concat(dfs)

        updates_df.rename(columns={
            'm': 'moment',
            'b': 'bikes',
            's': 'spaces'
        }, inplace=True)

        updates_df.set_index('moment', inplace=True)
        updates_df.groupby(updates_df.index, sort=False).first()

        return updates_df

    def __repr__(self):
        return '<Station #{}>'.format(self.id)

    def __str__(self):
        return '<{}>'.format(self.name)

    @property
    def has_regressor(self):
        '''
        Returns a boolean indicating if the station has an associated regressor (`True`) or not
        (`False`).
        '''
        return check_regressor_exists(self.city.slug, self.slug)

    def predict(self, kind, moment):
        '''
        Predict the number of bikes/spaces at a certain date.

        Args:
            kind (str): Indicate if the predict is for "bikes" or "spaces".
            moment (datetime.datetime): Indicate at which time the prediction should be made for.
                Corresponding features will be fetched.

        Returns:
            float: The prediction.
        '''
        regressor = load_regressor(self.city.slug, self.slug)
        features = munging.prepare(pd.DataFrame(index=[moment]))
        bikes = regressor.predict(features)[0]

        # Docks = bikes + spaces
        if kind == 'spaces':
            return self.docks - bikes
        return bikes

    def distance(self, latitude, longitude):
        '''
        Calculate the great-circle distance from the station to a given point defined by it's
        longitudinal position.

        Args:
            lat (float): Decimal latitude of the point.
            lon (float): Decimal longitude of the point.

        Returns:
            float: The distance in meters.
        '''

        return util.compute_haversine_distance(self.latitude, self.longitude, latitude, longitude)


class Training(db.Model):
    __tablename__ = 'trainings'

    backward = Column(Integer, CheckConstraint('0 < backward'), nullable=False, index=True)
    error = Column(Float, CheckConstraint('0 <= error'), nullable=False, index=True)
    forward = Column(Integer, CheckConstraint('0 < forward'), nullable=False, index=True)
    id = Column(Integer, primary_key=True, autoincrement=True)
    moment = Column(DateTime, nullable=False, index=True)

    station = relationship('Station', back_populates='training')
    station_id = Column(Integer, ForeignKey('stations.id', ondelete='CASCADE'), nullable=False, index=True)

    def __repr__(self):
        return '<Training #{}>'.format(self.id)

    def __str__(self):
        return '<Training for {} at {}>'.format(self.station.name, self.moment)


class Forecast(db.Model):
    __tablename__ = 'forecasts'

    at = Column(DateTime, nullable=False, index=True) # When the forecast was made at
    id = Column(Integer, primary_key=True, autoincrement=True)
    kind = Column(String, CheckConstraint("kind IN ('bikes', 'spaces')"), nullable=False, index=True)
    moment = Column(DateTime, nullable=False, index=True) # When the forecast was made for
    observed = Column(Integer, CheckConstraint('0 <= observed'))
    predicted = Column(Integer, CheckConstraint('0 <= predicted'), nullable=False, index=True)
    expected_error = Column(Float, CheckConstraint('0 <= expected_error'), nullable=False, index=True)

    station = relationship('Station', back_populates='forecasts')
    station_id = Column(Integer, ForeignKey('stations.id', ondelete='CASCADE'), nullable=False, index=True)

    __table_args__ = (
        CheckConstraint('at <= moment', name='ck_forecast_time_coherence'),
    )

    def __repr__(self):
        return '<Forecast #{}>'.format(self.id)

    def __str__(self):
        return '<{} forecast for {} done for {}>'.format(self.kind.capitalize(), self.station.name, self.moment)
