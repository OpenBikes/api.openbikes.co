import pandas as pd


def split(dataframe, target, ignored=['spaces']):
    ''' Split the features from the target. '''
    features = [
        column
        for column in dataframe.columns
        if column not in [target] + ignored
    ]
    X = dataframe[features]
    Y = dataframe[target].ravel()
    return X, Y


def extract_date_features(date):
    ''' Extract relevant time information from a date. '''
    features = {
        'hour': date.hour,
        'minute': date.minute,
        'weekday': date.weekday()
    }
    return features


def prepare(dataframe):
    ''' Extract features and label them as categorical or numerical. '''
    # Just to be sure, drop the duplicates
    dataframe = dataframe.groupby(dataframe.index).first()
    # Extract features
    features = pd.DataFrame([
        extract_date_features(date)
        for date in dataframe.index
    ])
    features.set_index(dataframe.index, inplace=True)
    dataframe = dataframe.join(features)
    return dataframe
