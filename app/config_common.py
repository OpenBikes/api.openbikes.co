import variables

# Secret key for generating tokens
SECRET_KEY = variables.APP_SECRET

# Folders
STATIC_FOLDER = 'app/static/'
GEOJSON_FOLDER = 'collecting/geojson'
REGRESSORS_FOLDER = 'training/regressors'

# Database URI
SQLALCHEMY_DATABASE_URI = 'postgresql://{user}:{pwd}@{service}:{port}/{name}'.format(
    user=variables.POSTGRESQL_USER,
    service=variables.POSTGRESQL_SERVICE,
    pwd=variables.POSTGRESQL_PWD,
    port=variables.POSTGRESQL_PORT,
    name=variables.POSTGRESQL_DBNAME
)
SQLALCHEMY_TRACK_MODIFICATIONS = True

# Logger settings
LOG_FILENAME = 'activity.log'
LOG_MAXBYTES = 10e9
LOG_BACKUPS = 3
