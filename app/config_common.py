import keys

# Secret key for generating tokens
SECRET_KEY = keys.APP_SECRET

# Folders
STATIC_FOLDER = 'app/static/'
GEOJSON_FOLDER = 'collecting/geojson'
REGRESSORS_FOLDER = 'training/regressors'

# Database URI
SQLALCHEMY_DATABASE_URI = 'postgresql://{user}:{pwd}@localhost:{port}/{name}'.format(
    user='postgres',
    pwd=keys.POSTGRESQL_PWD,
    port=5433,
    name='openbikes'
)
SQLALCHEMY_TRACK_MODIFICATIONS = True

# Logger settings
LOG_FILENAME = 'activity.log'
LOG_MAXBYTES = 10e9
LOG_BACKUPS = 3

