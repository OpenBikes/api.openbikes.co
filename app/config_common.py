import os

from dotenv import load_dotenv, find_dotenv


load_dotenv(find_dotenv())

# API keys
GOOGLE_ELEVATION_API_KEY = os.environ.get('GOOGLE_ELEVATION_API_KEY')
GOOGLE_DISTANCE_MATRIX_API_KEY = os.environ.get('GOOGLE_DISTANCE_MATRIX_API_KEY')
OPEN_WEATHER_MAP_API_KEY = os.environ.get('OPEN_WEATHER_MAP_API_KEY')
JCDECAUX_API_KEY = os.environ.get('JCDECAUX_API_KEY')
KEOLIS_API_KEY = os.environ.get('KEOLIS_API_KEY')
LACUB_API_KEY = os.environ.get('LACUB_API_KEY')

# Secret key for generating tokens
SECRET_KEY = os.environ.get('APP_SECRET') or 'houdini'

SQLALCHEMY_TRACK_MODIFICATIONS = os.environ.get('SQLALCHEMY_TRACK_MODIFICATIONS', False)

MONGO_HOST = os.environ.get('MONGO_HOST', 'mongo')
MONGO_PORT = int(os.environ.get('MONGO_PORT', 27017))

REGRESSORS_FOLDER = os.environ.get('REGRESSORS_FOLDER', 'training/regressors/')

# Postgres credentials
POSTGRES_USER = os.environ.get('POSTGRES_USER', 'postgres')
POSTGRES_PASS = os.environ.get('POSTGRES_PASS', 'postgres')
POSTGRES_HOST = os.environ.get('POSTGRES_HOST', 'postgres')
POSTGRES_PORT = int(os.environ.get('POSTGRES_PORT', 5432))
POSTGRES_DBNAME = os.environ.get('POSTGRES_DBNAME', 'openbikes')

# Postgres connexion
SQLALCHEMY_DATABASE_URI = 'postgresql://{user}:{pwd}@{host}:{port}/{name}'.format(
    user=POSTGRES_USER,
    pwd=POSTGRES_PASS,
    host=POSTGRES_HOST,
    port=POSTGRES_PORT,
    name=POSTGRES_DBNAME
)

TIMEZONE = 'Europe/Paris'

# Logger settings
LOG_MAXBYTES = 10e8  # 100 MB
LOG_BACKUPS = 3
