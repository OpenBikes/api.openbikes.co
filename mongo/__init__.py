from pymongo import MongoClient

from app import app


client = MongoClient(app.config['MONGO_HOST'], app.config['MONGO_PORT'])
