import os
from zipfile import ZipFile

import pickle

from app import app


def save_regressor(regressor, city, station):
    '''
    Save a regressor. The function starts by making a pickle
    file and then makes a zipfile. Finally it deletes the
    pickle file.
    '''
    directory = os.path.join(
        os.environ.get('REGRESSORS_FOLDER'),
        city
    )
    if not os.path.exists(directory):
        os.makedirs(directory)
    path = os.path.join(directory, station.replace('/', '_'))
    # Destroy the zipfile if it already exists
    try:
        os.remove('{0}.zip'.format(path))
    except:
        pass
    # Save the regressor
    with open('{0}.pkl'.format(path), 'wb') as outfile:
        pickle.dump(regressor, outfile)
    # Zip it
    with ZipFile('{0}.zip'.format(path), 'w') as zipped:
        zipped.write('{0}.pkl'.format(path))
    # Destroy it
    os.remove('{0}.pkl'.format(path))


def load_regressor(city, station):
    ''' Load a regressor in memory. '''
    path = os.path.join(
        os.environ.get('REGRESSORS_FOLDER'),
        city,
        station.replace('/', '_')
    )
    with ZipFile('{0}.zip'.format(path)) as zf:
        zf.extractall()
    with open('{0}.pkl'.format(path), 'rb') as infile:
        os.remove('{0}.pkl'.format(path))
        regressor = pickle.load(infile)
        return regressor
