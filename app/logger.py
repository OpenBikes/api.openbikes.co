'''
logger.py customizes the app's logging module. Each time an event is logged the logger
checks the level of the event (eg. debug, warning, info...). If the event is
above the approved threshold then it goes through. The handlers do the same thing;
They output to a file/shell if the event level is above their threshold.

:Example:

        >>> from website import app
        >>> app.logger.info('Hello')
        >>> app.logger.warning('Testing %s', 'foo')

**Levels**:
        - app.logger.debug('For debugging purposes')
        - app.logger.info('An event occured, for example a database update')
        - app.logger.warning('Rare situation')
        - app.logger.error('Something went wrong')
        - app.logger.critical('Very very bad')
'''

import logging

from app import app

# Set the logging level
app.logger.setLevel(app.config['LOG_LEVEL'])

# Create a formatter which defines the layout of each record
formatter = logging.Formatter('%(asctime)s :: %(levelname)s :: %(filename)s:%(lineno)s :: %(message)s')

# Add a handler to write log messages to a file
file_handler = logging.handlers.RotatingFileHandler(app.config['LOG_FILENAME'],
						    app.config['LOG_MAXBYTES'],
						    app.config['LOG_BACKUPS'])
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
app.logger.addHandler(file_handler)
