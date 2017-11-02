<div align="center">
  <img src="https://docs.google.com/drawings/d/1Q3qpaYW0OS3a0fcBObYDxwkp_vco-K92WNFwJ9Wflcc/pub?w=491&h=179" alt="logo"/>
</div>

## Environment file

```sh
GOOGLE_ELEVATION_API_KEY=https://developers.google.com/maps/documentation/elevation
GOOGLE_TIME_ZONE_API_KEY=https://developers.google.com/maps/documentation/timezone

OPEN_WEATHER_MAP_API_KEY=http://openweathermap.org/api

JCDECAUX_API_KEY=https://developer.jcdecaux.com/
KEOLIS_API_KEY=https://data.keolis-rennes.com/fr/accueil.html
LACUB_API_KEY=http://data.bordeaux-metropole.fr/apicub

SECRET_KEY=keep_it_secret_keep_it_safe

POSTGRES_NAME=openbikes
POSTGRES_USER=postgres
POSTGRES_PASS=postgres
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
```

## Installation

1. Install Python
2. Install PostgreSQL
3. `pip install -r requirements.txt`
4. `python manage.py migrate`

## Management

```sh
python manage.py help
```

## To do

- Finish adding APIs
- Finish federated API
