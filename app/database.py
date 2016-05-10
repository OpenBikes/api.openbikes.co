from sqlalchemy import create_engine
import contextlib
import sqlalchemy.exc

from app import app
from app import db


engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'],
                       echo=app.config['DATABASE_ECHO'])

# Use Flask-Alchemy's base model
Model = db.Model
session = db.session


def init_db():
    ''' Create the database. '''
    uri = app.config['SQLALCHEMY_DATABASE_URI'].split('/')
    url = '/'.join(uri[:-1])
    name = uri[-1]
    with contextlib.suppress(sqlalchemy.exc.ProgrammingError):
        with create_engine(url, isolation_level='AUTOCOMMIT').connect() as conn:
            conn.execute("CREATE DATABASE {} WITH encoding='utf-8'".format(name))
    # Add postgis extension
    session.execute('CREATE EXTENSION postgis')
    session.commit()
    Model.metadata.create_all(bind=engine)


def drop_db():
    ''' Delete the database. '''
    uri = app.config['SQLALCHEMY_DATABASE_URI'].split('/')
    url = '/'.join(uri[:-1])
    name = uri[-1]
    with contextlib.suppress(sqlalchemy.exc.ProgrammingError):
        with create_engine(url, isolation_level='AUTOCOMMIT').connect() as conn:
            conn.execute('DROP DATABASE {}'.format(name))
