'''Holds connection logic and utilities for the PSQL database'''


from os import environ
import psycopg2 # TODO add this to requirements.txt


DB_URI = 'DATABASE_URL'


def get_connection():
    ''' Creates and returns a new connection to the postgres database.
    '''
    url = _try_get_url()
    if url:
        # Parse the URI and create a connection
        connection_params_dict = psycopg2.extensions.parse_dsn(url)
        return psycopg2.connect(**connection_params_dict)
    else:
        # TODO log a message and return None or throw an exception
        print('Unable to read URL from environment')
        return None


def _try_get_url():
    '''Tries to read the URI for the database from the environment
    '''
    try:
        return environ[DB_URI]
    except:
        return None


def get_test_table_contents(connection=None):
    ''' Returns the full contents of the test table.

    If no connection is provided, a new one is created for this task.
    '''
    if not connection:
        connection = get_connection()
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM test_table;')
    return cursor.fetchall()
