import os

from dotenv import load_dotenv
from app.util import try_keys

load_dotenv('.env')

# Secret key for generating tokens
SECRET_KEY = os.environ.get('APP_SECRET') or 'houdini'

# Postges credentials
POSTGRES_USER = try_keys(os.environ, ['POSTGRES_USER'], 'postgres')
POSTGRES_PASS = try_keys(os.environ, ['POSTGRES_PASS'], 'postgres')
POSTGRES_HOST = try_keys(os.environ, ['POSTGRES_HOST'], 'postgres')
POSTGRES_PORT = try_keys(os.environ, ['POSTGRES_PORT'], 5433)
POSTGRES_DBNAME = try_keys(os.environ, ['POSTGRES_DBNAME'], 'openbikes')

# Postgres connexion
SQLALCHEMY_DATABASE_URI = 'postgresql://{user}:{pwd}@{host}:{port}/{name}'.format(
    user=POSTGRES_USER,
    pwd=POSTGRES_PASS,
    host=POSTGRES_HOST,
    port=POSTGRES_PORT,
    name=POSTGRES_DBNAME
)

SQLALCHEMY_TRACK_MODIFICATIONS = os.environ.get('SQLALCHEMY_TRACK_MODIFICATIONS') or True

GEOJSON_FOLDER = try_keys(os.environ, ['GEOJSON_FOLDER'], 'collecting/geojson/')
REGRESSORS_FOLDER = try_keys(os.environ, ['REGRESSORS_FOLDER'], 'training/regressors/')

TIMEZONE = 'Europe/Paris'

# Logger settings
LOG_MAXBYTES = 10e8  # 100 MB
LOG_BACKUPS = 3
