import sys, os

sys.path.insert(0, '/var/www/api.openbikes.co')
os.chdir('/var/www/api.openbikes.co')

from app import app

application = app
