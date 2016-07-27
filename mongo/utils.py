import subprocess
from pymongo import MongoClient


def mongo_conn():
    # Create a SSH tunnel in the background
    tunnel_command = 'ssh -f -N -L 2000:localhost:27017 46.101.234.224 -l max'
    try:
        subprocess.call(tunnel_command, shell=True)
    except Exception as err:
        print('Port 2000 is already in use.')
    return MongoClient(port=2000)
