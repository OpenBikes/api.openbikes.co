# OpenBikes API

![logo](https://github.com/OpenBikes/meta/blob/master/logo.png)

## Environment variables

Whatever the setup target (development or production, local or distant, with or without Docker), **add a `.env` file** with the following variables (no quotes needed).

```sh
GOOGLE_ELEVATION_API_KEY=https://developers.google.com/maps/documentation/elevation
GOOGLE_DISTANCE_MATRIX_API_KEY=https://developers.google.com/maps/documentation/distance-matrix

OPEN_WEATHER_MAP_API_KEY=http://openweathermap.org/api

JCDECAUX_API_KEY=https://developer.jcdecaux.com/#/opendata/vls?page=getstarted
KEOLIS_API_KEY=https://data.keolis-rennes.com/fr/accueil.html
LACUB_API_KEY=http://data.bordeaux-metropole.fr/apicub

REGRESSORS_FOLDER=training/regressors/

MONGO_HOST=mongo
MONGO_PORT=27017

APP_SECRET=secret

POSTGRES_USER=postgres
POSTGRES_PASS=postgres
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DBNAME=openbikes
```

## Running in production

Follow the [installation script](install.sh).

## Running locally

### Install Python

Because we scientific libraries for doing machine learning, we recommend using [Anaconda](https://www.continuum.io/why-anaconda)'s Python 3 distribution. You can download it [here](https://www.continuum.io/downloads). A good idea is then to create virtual environment:

```sh
cd ~/path/to/api.openbikes.co/
conda create -n venv python=3.4 anaconda
source activate venv
make install
```

### Install MongoDB

Refer to the official [documentation](https://docs.mongodb.com/manual/installation/#mongodb-community-edition).

### Install PostgreSQL + PostGIS

Stick with PostgreSQL 9.3/9.4 and PostGIS 2.1/2.2.

### Run the application

```sh
cd ~/path/to/api.openbikes.co/
make dev
python3 manage.py initdb
./scripts/add-cities.sh
python3 manage.py runserver
```

## Managing the application

- `python3 manage.py -h` to get a list of available commands.
- `python3 collect-bikes.py` to get current biking data.
- `python3 collect-weather.py` to get current weather data.
- `python3 train-regressors.py` to train regressors.
- `python3 scripts/import-dump.py <city>` to fetch and load a dump from the production server for the given city.
- `python3 scripts/create-dataset.py <city>` to create a dataset containing positions, weather and biking data for the given city.
