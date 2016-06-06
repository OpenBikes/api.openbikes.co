# OpenBikes API

## Environment variables

Whatever the setup target (development or production), with or without Docker, **add a `.env` file** with the following variables (no quotes needed).

```sh
GOOGLE_ELEVATION_API_KEY=https://developers.google.com/maps/documentation/elevation
GOOGLE_DISTANCE_MATRIX_API_KEY=https://developers.google.com/maps/documentation/distance-matrix

OPEN_WEATHER_MAP_API_KEY=http://openweathermap.org/api

JCDECAUX_API_KEY=https://developer.jcdecaux.com/#/opendata/vls?page=getstarted
KEOLIS_API_KEY=https://data.keolis-rennes.com/fr/accueil.html
LACUB_API_KEY=http://data.bordeaux-metropole.fr/apicub

APP_SECRET=secret

POSTGRES_USER=postgres
POSTGRES_PASS=postgres
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DBNAME=openbikes
```

## Running Docker

Install the [Docker toolbox](https://www.docker.com/products/docker-toolbox) and then run the following commands for either running Docker locally or in production. Don't forget to `docker commit` when applying changes to a container.

### Locally

```sh
docker-machine create -d virtualbox dev
docker-machine env dev
eval "$(docker-machine env dev)"
docker-compose build
docker-compose up -d
docker-compose run web make dev
```

- Don't forget to `docker-machine stop dev` when you're done so that the container stops running in the background.
- Use `docker-machine start dev` to boot up the dev container the next time you want to use it.
- If you encounter a problem then you can `docker-machine rm dev` and start again.
- A good internet connection makes the process painless.

### In production

## Running locally
