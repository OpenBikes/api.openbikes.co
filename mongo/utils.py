import subprocess

from pymongo import MongoClient


def create_remote_connexion(port=2000):
    # Create a SSH tunnel in the background
    tunnel_command = 'ssh -f -N -L {}:localhost:27017 46.101.234.224 -l max'.format(port)
    try:
        subprocess.call(tunnel_command, shell=True)
    except Exception as err:
        print('Port {} is already in use'.format(port))
    return MongoClient(port=port)
