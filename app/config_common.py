import os
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

# Secret key for generating tokens
SECRET_KEY = os.environ.get('APP_SECRET')

# Folders
GEOJSON_FOLDER = 'collecting/geojson'
REGRESSORS_FOLDER = 'training/regressors'

# Database URI
SQLALCHEMY_DATABASE_URI = 'postgresql://{user}:{pwd}@{service}:{port}/{name}'.format(
    user=os.environ.get('POSTGRESQL_USER'),
    service=os.environ.get('POSTGRESQL_SERVICE'),
    pwd=os.environ.get('POSTGRESQL_PWD'),
    port=os.environ.get('POSTGRESQL_PORT'),
    name=os.environ.get('POSTGRESQL_DBNAME')
)
SQLALCHEMY_TRACK_MODIFICATIONS = True

# Logger settings
LOG_FILENAME = 'activity.log'
LOG_MAXBYTES = 10e9
LOG_BACKUPS = 3
