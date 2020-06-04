'''Provides functions to create a WebDriver using the current environment.

This module relies on the presence of environment variables which point to the
binaries for Google Chrome and the Chrome web driver.

The Chrome "buildpack" for heroku defines the location of the Chrome binary as
'GOOGLE_CHROME_SHIM'.
See https://github.com/heroku/heroku-buildpack-google-chrome.

The path to the Chrome web driver binary must be stored in environment variable
CHROMEDRIVER_PATH. This has been set as a "Config Var" on Heroku.

For local development, you will need to install both Chrome and the ChromeDriver
(https://chromedriver.chromium.org/downloads) and set the above environment
variables to the correct locations.
'''

import logging
from os import environ
import selenium.webdriver

LOGGER = logging.getLogger(__name__)

# Environment variables
GOOGLE_CHROME_BINARY = 'GOOGLE_CHROME_SHIM'
CHROMEDRIVER_BINARY = 'CHROMEDRIVER_PATH'


def get_webdriver(headless=True):
    '''Creates and returns a selenium webdriver'''
    return _get_chromedriver(headless)


def _get_chromedriver(headless):
    '''Creates and returns a ChromeDriver'''
    opts = selenium.webdriver.ChromeOptions()
    opts.headless = headless
    chrome_bin = _try_get_chome_binary_path()
    opts.binary_location = chrome_bin

    chromedriver_path = _try_get_chromedriver_path()
    chrome_driver = selenium.webdriver.Chrome(chromedriver_path, options=opts)

    # Allow for a small amount of latency for each action
    chrome_driver.implicitly_wait(1)

    LOGGER.info("Created ChromeDriver")
    return chrome_driver


def _try_get_chromedriver_path():
    '''Returns the path to the executable for the Chrome WebDriver using the
    environment or raises a KeyError.
    '''
    return _try_get_env_var(CHROMEDRIVER_BINARY)



def _try_get_chome_binary_path():
    '''Returns the path to the executable for Chrome using the environment or
    raises a KeyError.'''
    return _try_get_env_var(GOOGLE_CHROME_BINARY)


def _try_get_env_var(name):
    '''Tries to read the given variable from the environment

    If no such variable is defined, a KeyError is raised and an error message
    is logged.
    '''
    try:
        return environ[name]
    except KeyError:
        LOGGER.error("No '%s' environment variable set", name)
        raise
