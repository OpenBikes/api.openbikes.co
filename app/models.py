import json

from geoalchemy2 import Geometry
import pandas as pd
from sqlalchemy import (
    CheckConstraint, Column, Integer, String, Boolean, DateTime, Float,
    ForeignKey, Text
)
from sqlalchemy.orm import relationship

from app import util
from app.database import Model
from training.util import check_regressor_exists, load_regressor
from training import munging


class City(Model):
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

    @property
    def geojson(self):
        return json.loads(self._geojson)

    @geojson.setter
    def geojson(self, value):
        self._geojson = json.dumps(value)

    def __repr__(self):
        return '<City {}>'.format(self.name)


class Station(Model):
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

    def __repr__(self):
        return '<Station {}>'.format(self.name)

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


class Training(Model):
    __tablename__ = 'trainings'

    backward = Column(Integer, CheckConstraint('0 < backward'), nullable=False, index=True)
    error = Column(Float, CheckConstraint('0 <= error'), nullable=False, index=True)
    forward = Column(Integer, CheckConstraint('0 < forward'), nullable=False, index=True)
    id = Column(Integer, primary_key=True, autoincrement=True)
    moment = Column(DateTime, nullable=False, index=True)

    station = relationship('Station', back_populates='training')
    station_id = Column(Integer, ForeignKey('stations.id', ondelete='CASCADE'), nullable=False, index=True)

    def __repr__(self):
        return '<Training for {} on {}>'.format(self.station, self.moment)


class Forecast(Model):
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
        return '<Forecast of {} for {} on {}>'.format(self.kind, self.station, self.moment)
