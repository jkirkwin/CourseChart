'''Holds connection logic and utilities for the PSQL database'''

import logging
from os import environ
import psycopg2


# TODO update logging to work for multiple processes
LOGGER = logging.getLogger(__name__)


DB_URI = 'DATABASE_URL'


def connect(url=None):
    ''' Creates and returns a new connection to the postgres database.

        If no URL is provided, use the DATABASE_URL environment variable.
    '''
    if url is None:
        envUrl = _try_get_url()
        if envUrl is None:
            raise EnvironmentError('Unable to read URL from environment')
        url = envUrl
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
        connection = connect()

    cursor = connection.cursor()
    cursor.execute('SELECT * FROM test_table;')
    for row in cursor.fetchall():
        print(row)
