import datetime as dt

from bs4 import BeautifulSoup


def epoch_to_datetime(epoch, divisor=1):
    ''' Convert a UNIX timestamp to ISO formatted time. '''
    moment = dt.datetime.fromtimestamp(round(epoch / divisor))
    return moment


def load_xml(string):
    ''' Convenience wrapper for the BeautifulSoup library. '''
    return BeautifulSoup(string, 'lxml')


def extract_element(element, child):
    '''
    Extract the content of a child element from an XML element.
    '''
    value = element.find(child)
    if type(value) is None:
        return ''
    elif not value:
        return ''
    else:
        return value.string


def extract_attribute(element, attribute):
    ''' Extract an attribute from an XML element. '''
    value = element.get(attribute)
    return value