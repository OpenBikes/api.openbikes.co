import binascii
import os
import sys
import time

from app.util import FloatConverter

from flask import Flask, request, session
from flask_sqlalchemy import SQLAlchemy
from pymongo import MongoClient
from sqlalchemy import event
from sqlalchemy.engine import Engine

app = Flask(__name__, static_folder='static', static_url_path='')


# Configure the application
app.config.from_object('app.config_common')
app.config.from_object('app.config')

# The built-in FloatConverter does not handle negative numbers.
app.url_map.converters['float'] = FloatConverter

# Create an SQLAlchemy binding
db = SQLAlchemy(app)

# Set the MongoDB client
mongo_client = MongoClient(app.config['MONGO_HOST'], app.config['MONGO_PORT'])
mongo_bikes_coll = mongo_client[app.config['MONGO_BIKES_COLLECTION_NAME']]
mongo_weather_coll = mongo_client[app.config['MONGO_WEATHER_COLLECTION_NAME']]

# Add the top level to the import path
sys.path.append('..')

# Import the views
from app.views import api, main
app.register_blueprint(api.API_BP)

# Setup the logger
from app.logger_setup import logger

# Create the necessary folders if they don't exist
if not os.path.exists(app.config['REGRESSORS_FOLDER']) and os.getcwd().split('/')[-1] not in ('analysis', 'scripts'):
    os.makedirs(app.config['REGRESSORS_FOLDER'])

# Configure session shutdown
@app.teardown_appcontext
def shutdown_session(exception=None):
    db.session.remove()


@app.before_request
def before_request():

    # For measuring the wall-clock time of a request
    request.start_time = time.time()

    # Create a session ID by generating a random hex value
    if not session.get('session_id'):
        session['session_id'] = str(binascii.b2a_hex(os.urandom(3)))


@app.after_request
def after_request(response):

    log = logger.new(
        endpoint=request.endpoint,
        method=request.method,
        path=request.path,
        args=request.args,
        status_code=response.status_code
    )

    # Try to serialize the request data into the log entry
    if request.data:
        log = log.bind(data=request.get_json(silent=True))

    # Measure response time
    log = log.bind(response_time=round(time.time() - request.start_time, 5))
    if hasattr(request, 'queries_count') and hasattr(request, 'queries_duration'):
        log = log.bind(queries_count=request.queries_count)
        log = log.bind(queries_duration=round(request.queries_duration, 5))

    log.info(u'HTTP request')

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
