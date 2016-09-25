import click
import datetime as dt
import time

from termcolor import colored

DATE_FORMAT = '%Y/%m/%d-%H:%M:%S'


def notify(message, color, start_time=None):
    if start_time:
        now = dt.timedelta(seconds=time.time() - start_time)
        print(colored('{} - {}'.format(now, message), color))
    else:
        print(colored(message, color))


class DateParamType(click.ParamType):
    name = 'date'

    def convert(self, value, param, ctx):
        try:
            return dt.datetime.strptime(value, '%Y/%m/%d-%H:%M:%S')
        except ValueError:
            self.fail('{val} is not a valid date (format: {fmt})'.format(
                val=value, fmt=DATE_FORMAT))
