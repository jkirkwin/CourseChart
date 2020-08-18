'''Holds connection logic and utilities for the PSQL database'''

import logging
from os import environ
import psycopg2 # TODO add this to requirements.txt


LOGGER = logging.getLogger(__name__)


DB_URI = 'DATABASE_URL'


def get_connection():
    ''' Creates and returns a new connection to the postgres database.
    '''
    url = _try_get_url()
    if not url:
        raise EnvironmentError('Unable to read URL from environment')

    return connect_to_url(url)


def connect_to_url(url):
    ''' Creates and returns a new connection to the postgres database at the given URI.
    '''
    try:
        connection_params_dict = psycopg2.extensions.parse_dsn(url)
        connection = psycopg2.connect(**connection_params_dict)
        LOGGER.info("Created PSQL connection")
        return connection
    except:
        LOGGER.error('Unable to connect to PSQL database with URI')
        raise


def _try_get_url():
    '''Tries to read the URI for the database from the environment
    '''
    try:
        return environ[DB_URI]
    except KeyError:
        LOGGER.warning("Unable to read environment variable '%s'", DB_URI)
        return None


def print_test_table(connection=None):
    ''' Prints the full contents of the test table.

    If no connection is provided, a new one is created for this task.
    '''
    if not connection:
        connection = get_connection()

    cursor = connection.cursor()
    cursor.execute('SELECT * FROM test_table;')
    for row in cursor.fetchall():
        print(row)
