import math

from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, Float, ForeignKey,
    CheckConstraint
)
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry
import pandas as pd

from app.database import Model
from training import util
from training import munging


class City(Model):
    __tablename__ = 'cities'

    active = Column(Boolean, nullable=False, index=True)
    country = Column(String, nullable=False, index=True)
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

    stations = relationship('Station', back_populates='city')

    def __repr__(self):
        return '<City %r>' % self.name


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
    city_id = Column(Integer, ForeignKey('cities.id'), nullable=False, index=True)

    training = relationship('Training', uselist=False)

    predictions = relationship('Prediction', back_populates='station', lazy='dynamic')

    def __repr__(self):
        return '<Station %r>' % self.name

    def predict(self, kind, date):
        '''
        Predict the number of bikes/spaces at a certain date.

        Args:
            kind (str): Indicate if the predict is for "bikes" or "spaces".
            date (datetime.datetime): Indicate at which time the prediction
                should be made for. Corresponding features will be fetched.

        Returns:
            float: The prediction.
        '''
        regressor = util.load_regressor(self.city.slug, self.slug)
        features = munging.prepare(pd.DataFrame(index=[date]))
        bikes = regressor.predict(features)[0]
        # Docks = bikes + spaces
        if kind == 'spaces':
            return self.docks - bikes
        return bikes

    def distance(self, lat, lon):
        '''
        Calculate the great-circle distance from the station to a given point
        defined by it's longitudinal position.

        Args:
            lat (float): Decimal latitude of the point.
            lon (float): Decimal longitude of the point.

        Returns:
            float: The distance in meters.
        '''
        # Convert decimal degrees to radians
        lat1, lon1, lat2, lon2 = map(
            math.radians,
            [self.latitude, self.longitude, lat, lon]
        )
        # Apply Haversine formula
        a = (math.sin((lat2 - lat1) / 2) ** 2 +
             math.cos(lat1) * math.cos(lat2) * math.sin((lon2 - lon1) / 2) ** 2)
        c = 2 * math.asin(math.sqrt(a))
        # 6371000 meters is the mean radius of the Earth
        distance = 6371000 * c
        return distance


class Training(Model):
    __tablename__ = 'trainings'

    backward = Column(Integer, CheckConstraint('0 < backward'), nullable=False, index=True)
    error = Column(Float, CheckConstraint('0 <= error'), nullable=False, index=True)
    forward = Column(Integer, CheckConstraint('0 < forward'), nullable=False, index=True)
    id = Column(Integer, primary_key=True, autoincrement=True)
    moment = Column(DateTime, nullable=False, index=True)

    station = relationship('Station', back_populates='training')
    station_id = Column(Integer, ForeignKey('stations.id'), nullable=False, index=True)

    def __repr__(self):
        return '<Training for %r on %r>' % self.station, self.moment


class Prediction(Model):
    __tablename__ = 'predictions'

    at = Column(DateTime, nullable=False, index=True)
    id = Column(Integer, primary_key=True, autoincrement=True)
    kind = Column(String, CheckConstraint("kind IN ('bikes', 'spaces')"), nullable=False, index=True)
    moment = Column(DateTime, nullable=False, index=True)
    observed = Column(Integer, CheckConstraint('0 < observed'))
    predicted = Column(Integer, CheckConstraint('0 < predicted'), nullable=False, index=True)

    station = relationship('Station', back_populates='predictions')
    station_id = Column(Integer, ForeignKey('stations.id'), nullable=False, index=True)

    __table_args__ = (
        CheckConstraint('at <= moment', name='ck_prediction_time_coherence'),
    )

    def __repr__(self):
        return '<Prediction %r for %r on %r>' % self.kind, self.station, self.date
