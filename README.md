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

## Running Docker

Install the [Docker toolbox](https://www.docker.com/products/docker-toolbox) and then run the following commands for either running Docker locally or in production.

### In development

```sh
cd ~/path/to/api.openbikes.co/
docker-machine create -d virtualbox --virtualbox-memory 512 --virtualbox-cpu-count 1 dev
docker-machine env dev
eval "$(docker-machine env dev)"
docker-compose build
docker-compose up -d
docker-compose run web make dev
docker-compose run web python3 manage.py initdb
docker-compose run web ./scripts/add-cities.sh
```

- Don't forget to `docker-machine stop dev` when you're done so that the container stops running in the background.
- Run `docker-machine start dev` to boot up the dev container the next time you want to use it.
- If you encounter a problem then you can `docker-machine rm dev` and start again.
- A good internet connection makes the process painless.
- You can access the application on the host by accessing `docker-machine ip dev`
- Access logs with `docker-compose logs`

__For Makefile aficionados__ :

```sh
cd ~/path/to/api.openbikes.co/
make docker.env
make docker.build
make docker.launch
docker-compose run web make dev
docker-compose run web python3 manage.py initdb
docker-compose run web ./scripts/add-cities.sh
```

For those who want to use Docker but don't like to type out VirtualBox IP you can update `/etc/hosts/` by adding a new alias for __`docker-env`__ :

```sh
$ cat /etc/hosts

##
# Host Database
#
# localhost is used to configure the loopback interface
# when the system is booting.  Do not change this entry.
##
127.0.0.1       localhost
255.255.255.255 broadcasthost
::1             localhost
xxx.xxx.xx.xxx  docker-dev
```

### In production

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
- `./scripts/import-dump.sh <city>` to fetch and load a dump from the production server for the given city.
