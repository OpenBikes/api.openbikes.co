from flask_script import Manager, prompt_bool, Shell, Server
from termcolor import colored

from app import app


manager = Manager(app)
manager.add_command('runserver', Server())

def make_shell_context():
    return dict(app=app)

manager.add_command('shell', Shell(make_context=make_shell_context))


@manager.command
def initdb():
    ''' Create the SQL database '''
    from app.database import init_db

    init_db()
    print(colored('The SQL database has been created', 'green'))


@manager.command
def dropdb():
    ''' Delete the SQL database. '''
    from app.database import drop_db

    if prompt_bool('Are you sure you want to lose all your SQL data?'):
        drop_db()
        print(colored('The SQL database has been deleted', 'green'))


@manager.option('-f', dest='provider', help='API provider script name')
@manager.option('-c', dest='city', help='City name')
@manager.option('-a', dest='city_api', help='City API name')
@manager.option('-o', dest='city_owm', help='City OpenWeatherMap name')
@manager.option('-p', dest='country', help='City belonging country')
@manager.option('-e', dest='predictable', help='Predictions enabled flag', default=False)
def addcity(provider, city, city_api, city_owm, country, predictable):
    ''' Add a city to the application '''
    import datetime as dt

    import numpy as np

    from app import models
    from app import services as srv
    from app import util
    from app.database import db_session_maker
    from collecting import util as collect_util
    from collecting import collect, google

    session = db_session_maker()
    # Check if the city is already in the database
    if models.City.query.filter_by(name=city).count() > 0:
        print(colored("'{}' has already been added".format(city), 'cyan'))
        return
    # Get the current information for a city
    try:
        stations = collect(provider, city_api)
    except:
        print(colored("Couldn't get stations data for '{}'".format(city), 'red'))
        return
    # Fetch the altitudes of every station
    try:
        altitudes = google.fetch_altitudes(stations)
    except:
        print(colored("Couldn't get altitudes for '{}'".format(city), 'red'))
        return
    # Add the city
    mean_lat = np.mean([station['latitude'] for station in stations])
    mean_lon = np.mean([station['longitude'] for station in stations])
    new_city = models.City(
        active=True,
        country=country,
        geojson=collect_util.json_to_geojson(stations),
        latitude=mean_lat,
        longitude=mean_lon,
        name=city,
        name_api=city_api,
        name_owm=city_owm,
        position='POINT({latitude} {longitude})'.format(latitude=mean_lat, longitude=mean_lon),
        predictable=predictable,
        provider=provider,
        slug=util.slugify(city),
        update=dt.datetime.now()
    )
    session.add(new_city)
    session.commit()
    # Add the stations and their initial training schedules
    srv.insert_stations(new_city, stations, altitudes)
    print(colored("'{}' has been added".format(city), 'green'))


@manager.command
def removecity(city):
    ''' Remove a city in the application '''
    from app import models
    from app.database import db_session_maker

    session = db_session_maker()
    # Check if the city is not in the database
    query = models.City.query.filter_by(name=city)
    if query.count() == 0:
        print(colored("'{}' doesn't exist".format(city), 'cyan'))
        return
    # Remove the city
    query.delete()
    session.commit()
    print(colored("'{}' has been removed".format(city), 'green'))


@manager.command
def updatecity(city):
    ''' Refresh a city in the application '''
    import numpy as np

    from app import models
    from app import services as srv
    from app.database import db_session_maker

    session = db_session_maker()
    # Check if the city is not in the database
    query = models.City.query.filter_by(name=city)
    if query.count() == 0:
        print(colored("'{}' doesn't exist".format(city), 'cyan'))
        return
    city = query.first()
    # Get the current information for a city
    try:
        stations = collect(city.provider, city.name_api)
    except:
        print(colored("Couldn't get stations data for '{}'".format(city.name), 'red'))
        return
    # Recalculate the center of the city
    mean_lat = np.mean([station['latitude'] for station in stations])
    mean_lon = np.mean([station['longitude'] for station in stations])
    city.latitude = mean_lat
    city.longitude = mean_lon
    city.position = 'POINT({latitude} {longitude})'.format(latitude=mean_lat, longitude=mean_lon)
    session.commit()
    # Delete the stations that don't exist anymore
    new_station_names = [station['name'] for station in stations]
    existing_stations = models.Station.query.filter_by(city_id=city.id)
    stations_to_delete = [
        station
        for station in existing_stations
        if station.name not in new_station_names
    ]
    for station in stations_to_delete:
        session.delete(station)
    session.commit()
    # Add the new stations
    old_station_names = [station.name for station in existing_stations]
    new_stations = [
        station
        for station in stations
        if station['name'] not in old_station_names
    ]
    try:
        altitudes = google.fetch_altitudes(new_stations)
    except:
        print(colored("Couldn't get altitudes for '{}'".format(city.name), 'red'))
        return
    srv.insert_stations(city, new_stations, altitudes)
    print(colored("'{}' has been updated, {} insertion(s), {} deletion(s)".format(
        city.name, len(new_stations), len(stations_to_delete)
    ), 'green'))


@manager.command
def disablecity(city):
    ''' Disable a city from the application '''
    from app import models
    from app.database import db_session_maker

    session = db_session_maker()
    # Check if the city is not in the database
    query = models.City.query.filter_by(name=city)
    if query.count() == 0:
        print(colored("'{}' doesn't exist".format(city), 'cyan'))
        return
    # Disable the city
    city = query.first()
    if not city.active:
        print(colored("'{}' is already disabled".format(city), 'cyan'))
        return
    city.active = False
    session.commit()
    print(colored("'{}' has been disabled".format(city), 'green'))


@manager.command
def enablecity(city):
    ''' Enable a city in the application '''
    from app import models
    from app.database import db_session_maker

    session = db_session_maker()
    # Check if the city is not in the database
    query = models.City.query.filter_by(name=city)
    if query.count() == 0:
        print(colored("'{}' doesn't exist".format(city), 'cyan'))
        return
    # Enable the city
    city = query.first()
    if city.active:
        print(colored("'{}' is already enabled".format(city), 'cyan'))
        return
    city.active = True
    session.commit()
    print(colored("'{}' has been enabled".format(city), 'green'))


@manager.command
def collectbikes():
    ''' Collect the bikes data for each active city. '''
    import datetime as dt

    from app import logger
    from app import models
    from app.database import db_session_maker
    from collecting import collect, util
    from mongo.timeseries import insert as insert_bikes

    session = db_session_maker()

    cities = models.City.query.filter_by(active=True)

    for city in cities:
        # Get the current data for a city
        try:
            stations = collect(city.provider, city.name_api)
        except:
            logger.warning("Couldn't retrieve station data", city=city.name)
            return
        # Update the database if the city can be predicted
        if city.predictable is True:
            insert_bikes.city(city.name, stations)
        # Save the data for the map
        city.geojson = util.json_to_geojson(stations)
        city.update = dt.datetime.now()
        session.commit()

    logger.info('Bike data collected')


@manager.command
def collectweather():
    ''' Collect the weather data for each active, predictable city. '''
    from app import logger
    from app import models
    from collecting import openweathermap as owm
    from mongo.weather import insert as insert_weather

    cities = models.City.query.filter_by(active=True, predictable=True)

    for city in cities:
        try:
            weather = owm.current(city.name_owm)
        except:
            logger.warning("Couldn't retrieve weather data", city=city.name)
            return
        insert_weather.city(city.name, weather)

    logger.info('Weather data collected')


@manager.command
def train():
    ''' Train a regressor for a station and save it. '''
    from sklearn.tree import DecisionTreeRegressor

    from app import logger
    from app import models
    from app.database import db_session_maker
    from training import util
    from training.optimization import bandit

    session = db_session_maker()

    method = DecisionTreeRegressor(max_depth=6)

    stations = models.Station.query

    for station in stations:
        # Train a regressor for the bikes and another one the spaces
        best = bandit(method, station.training)
        if not best:
            return
        # Update the database
        station.training.moment = best['moment']
        station.training.backward = best['backward']
        station.training.forward = best['forward']
        station.training.error = best['score']
        session.commit()
        # Save the regressor
        util.save_regressor(best['regressor'], station.city.slug, station.slug)

    logger.info('Regressors trained')


if __name__ == '__main__':
    manager.run()
