import os

from dotenv import load_dotenv

load_dotenv('.env')

# Secret key for generating tokens
SECRET_KEY = os.environ.get('APP_SECRET') or 'houdini'

# Postges credentials
POSTGRES_USER = os.environ.get('POSTGRES_USER', 'postgres')
POSTGRES_PASS = os.environ.get('POSTGRES_PASS', 'postgres')
POSTGRES_HOST = os.environ.get('POSTGRES_HOST', 'postgres')
POSTGRES_PORT = os.environ.get('POSTGRES_PORT', 5433)
POSTGRES_DBNAME = os.environ.get('POSTGRES_DBNAME', 'openbikes')

# Postgres connexion
SQLALCHEMY_DATABASE_URI = 'postgresql://{user}:{pwd}@{host}:{port}/{name}'.format(
    user=POSTGRES_USER,
    pwd=POSTGRES_PASS,
    host=POSTGRES_HOST,
    port=POSTGRES_PORT,
    name=POSTGRES_DBNAME
)

SQLALCHEMY_TRACK_MODIFICATIONS = os.environ.get('SQLALCHEMY_TRACK_MODIFICATIONS', True)

GEOJSON_FOLDER = os.environ.get('GEOJSON_FOLDER', 'collecting/geojson/')
REGRESSORS_FOLDER = os.environ.get('REGRESSORS_FOLDER', 'training/regressors/')

TIMEZONE = 'Europe/Paris'

# Logger settings
LOG_MAXBYTES = 10e8  # 100 MB
LOG_BACKUPS = 3
