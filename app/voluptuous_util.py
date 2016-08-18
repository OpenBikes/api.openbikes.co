import datetime as dt


def Timestamp():
    return lambda ts: dt.datetime.fromtimestamp(ts)
