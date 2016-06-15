import os

from dotenv import load_dotenv

load_dotenv('.env')

# Secret key for generating tokens
SECRET_KEY = os.environ.get('APP_SECRET')

# Postgres connexion
SQLALCHEMY_DATABASE_URI = 'postgresql://{user}:{pwd}@{host}:{port}/{name}'.format(
    user=os.environ.get('POSTGRES_USER'),
    pwd=os.environ.get('POSTGRES_PASS'),
    host=os.environ.get('POSTGRES_HOST'),
    port=os.environ.get('POSTGRES_PORT'),
    name=os.environ.get('POSTGRES_DBNAME')
)
SQLALCHEMY_TRACK_MODIFICATIONS = True

TIMEZONE = 'Europe/Paris'

# Logger settings
LOG_MAXBYTES = 10e8 # 100 MB
LOG_BACKUPS = 3
