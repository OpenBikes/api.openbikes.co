import datetime as dt

from flask.ext.script import Manager, Server, Shell, prompt_bool
import numpy as np
from termcolor import colored

from app import app
from app import models
from app import session
from app.database import init_db, drop_db
from collecting import collect
from collecting import google


manager = Manager(app)


manager.add_command('runserver', Server())

def make_shell_context():
    return dict(app=app)


manager.add_command('shell', Shell(make_context=make_shell_context))


@manager.command
def initdb():
	''' Create the SQL database '''
	# Create the physical database
	init_db()
	print(colored('The SQL database has been created', 'green'))


@manager.command
def dropdb():
	''' Delete the SQL database. '''
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
	# Check if the city is already in the database
	if 0 < models.City.query.filter_by(name=city).count():
		print(colored("'{}' has already been added".format(city), 'cyan'))
		return
	# Get the current information for a city
	try:
		stations = collect(provider, city_api)
	except:
		print(colored("Couldn't get stations data for '{}'".format(city), 'red'))
		return
	# Add the altitudes of every station
	try:
		altitudes = google.altitudes(stations)
	except:
		print(colored("Couldn't get altitudes for '{}'".format(city), 'red'))
		return
	# Add the city
	mean_lat = np.mean([station['latitude'] for station in stations])
	mean_lon = np.mean([station['longitude'] for station in stations])
	new_city = models.City(
		name=city,
		name_api=city_api,
		name_owm=city_owm,
		position='POINT({0} {1})'.format(mean_lat, mean_lon),
		latitude=mean_lat,
		longitude=mean_lon,
		predictable=predictable,
		active=True,
		country=country,
		provider=provider
	)
	session.add(new_city)
	session.flush()
	# Add the stations and their initial training schedules
	for station, altitude in zip(stations, altitudes):
		new_station = models.Station(
			name=station['name'],
			docks=station['bikes'] + station['stands'],
			position='POINT({0} {1})'.format(station['latitude'], station['longitude']),
			latitude=station['latitude'],
			longitude=station['longitude'],
			altitude=altitude['elevation'],
			city_id=new_city.id
		)
		session.add(new_station)
		session.flush()
		session.add(models.Training(
			moment=dt.datetime.now(),
			backward=7,
			forward=7,
			station_id=new_station.id,
			error=99
		))
	session.commit()
	# Notification
	print(colored("'{}' has been added".format(city), 'green'))


@manager.command
def disablecity(city):
	''' Disable a city in the application '''
	# Check if the city is not in the database
	query = models.City.query.filter_by(name=city)
	if query.count() == 0:
		print(colored("'{}' is not in the application".format(city), 'cyan'))
		return
	# Disable the city
	query.delete()
	session.commit()
	# Notification
	print(colored("{}' has been removed".format(city), 'green'))


@manager.command
def removecity(city):
	''' Remove a city from the application '''
	# Check if the city is not in the database
	query = models.City.query.filter_by(name=city)
	if query.count() == 0:
		print(colored('{} is not in the application'.format(city), 'cyan'))
		return
	# Remove the city
	city = query.first()
	city.active = False
	session.commit()
	# Notification
	print(colored("'{}' has been disabled".format(city), 'green'))


if __name__ == '__main__':
    manager.run()
