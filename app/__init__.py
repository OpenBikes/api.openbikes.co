import sys
import os

from flask import Flask
from flask_debugtoolbar import DebugToolbarExtension
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.profile import Profiler

app = Flask(__name__)

# Setup the application
app.config.from_object('app.config_common')
app.config.from_object('app.config')

# Debug toolbar
toolbar = DebugToolbarExtension(app)
Profiler(app)
db = SQLAlchemy(app)

# Add the top level to the import path
sys.path.append('..')

# Import the views
from app.views import (
    api
)
app.register_blueprint(api.API_BP)

# Setup the logger
from app import logger

# Setup the database
from app.database import session

# Configure session shutdown
@app.teardown_appcontext
def shutdown_session(exception=None):
    session.remove()

# Create the necessary folders if they don't exist
if not os.path.exists(app.config['GEOJSON_FOLDER']):
    os.makedirs(app.config['GEOJSON_FOLDER'])
if not os.path.exists(app.config['REGRESSORS_FOLDER']):
    os.makedirs(app.config['REGRESSORS_FOLDER'])
