import os

from sklearn.externals import joblib

from app import app


def save_regressor(regressor, city_slug, station_slug):
    '''
    Save a regressor. The function starts by making a pickle
    file and then makes a zipfile. Finally it deletes the
    pickle file.
    '''
    directory = os.path.join(app.config['REGRESSORS_FOLDER'], city_slug)
    if not os.path.exists(directory):
        os.makedirs(directory)
    path = os.path.join(directory, station_slug)
    # Destroy the zipfile if it already exists
    try:
        os.remove('{0}.zip'.format(path))
    except:
        pass
    # Save the regressor
    joblib.dump(regressor, '{}.pkl'.format(path), compress=3)


def load_regressor(city_slug, station_slug):
    ''' Load a regressor in memory. '''
    path = os.path.join(app.config['REGRESSORS_FOLDER'], city_slug, station_slug)
    file_name = '{0}.pkl'.format(path)
    regressor = joblib.load(file_name)
    return regressor


def check_regressor_exists(city_slug, station_slug):
    ''' Check if a regressor exists. '''
    path = os.path.join(app.config['REGRESSORS_FOLDER'], city_slug, station_slug)
    file_name = '{0}.pkl'.format(path)
    return os.path.isfile(file_name)
