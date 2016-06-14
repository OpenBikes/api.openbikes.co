import json
import os
import random
import sys
import time

from flask import Flask, request, session
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy import event
from sqlalchemy.engine import Engine

app = Flask(__name__)

# Configure the application
app.config.from_object('app.config_common')
app.config.from_object('app.config')

# Create an SQLAlchemy binding
db = SQLAlchemy(app)

# Add the top level to the import path
sys.path.append('..')


# Import the views
from app.views import (
    api
)
app.register_blueprint(api.API_BP)


# Setup the logger
from app.logger_setup import logger


# Setup the database
from app.database import db_session


# Configure session shutdown
@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


@app.before_request
def before_request():
    # Create a session ID by generating a random hex value
    if not session.get('session_id'):
        session['session_id'] = random.randint(0, 10e5)

    # For measuring the wall-clock time of a request
    request.start_time = time.time()

    data = {}
    if request.data:
        try:
            data = json.loads(request.data)
        except ValueError:
            data = request.data

    # Log the request with the attached args and body data
    logger.info(u'HTTP request',
                method=request.method,
                path=request.path,
                args=request.args,
                data=data)


@app.after_request
def measure_elapsed_time(response):
    elapsed_time = time.time() - request.start_time
    if elapsed_time > 0.2:
        logger.warning(u'Slow request',
                       endpoint=request.endpoint,
                       duration='{:.3f}'.format(elapsed_time),
                       queries_count=request.queries_count,
                       queries_duration='{:.3f}'.format(request.queries_duration))
    return response


@event.listens_for(Engine, 'before_cursor_execute')
def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    conn.info.setdefault('query_start_time', []).append(time.time())


@event.listens_for(Engine, 'after_cursor_execute')
def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    # Don't measure SQL queries execution time if outside of an HTTP request
    # context (because it has to be saved into the `request` object)
    if not request:
        return
    # Measure the query duration time
    elapsed_time = time.time() - conn.info['query_start_time'].pop(-1)
    # Add the duration to the current request object
    if hasattr(request, 'queries_count'):
        request.queries_count += 1
        request.queries_duration += elapsed_time
    else:
        request.queries_count = 1
        request.queries_duration = elapsed_time


# Create the necessary folders if they don't exist
if not os.path.exists(app.config['GEOJSON_FOLDER']):
    os.makedirs(app.config['GEOJSON_FOLDER'])
if not os.path.exists(app.config['REGRESSORS_FOLDER']):
    os.makedirs(app.config['REGRESSORS_FOLDER'])
