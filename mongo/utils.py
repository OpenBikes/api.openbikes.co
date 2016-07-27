import subprocess
from pymongo import MongoClient


def mongo_conn():
    # Create a SSH tunnel in the background
    tunnel_command = 'ssh -f -N -L 2000:localhost:27017 46.101.234.224 -l max'
    subprocess.call(tunnel_command, shell=True)
    return MongoClient(port=2000)

db = mongo_conn()
