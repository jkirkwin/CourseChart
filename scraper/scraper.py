'''Entry point script for the web scraper.

Uses Selenium to scrape the UVic academic calendar for course relationships 
and saves the information to the Postgres database
'''

import logging
from functools import partial
from multiprocessing import Pool
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from psycopg2 import sql
import driver_setup
import class_listing
import db


# TODO prevent Heroku from putting the app to sleep while the scraper is running.


# TODO Logging from sub-processes does not work.
# https://docs.python.org/3/howto/logging-cookbook.html#logging-to-a-single-file-from-multiple-processes
LOGGER = logging.getLogger(__name__)


# Scraping constants
BASE_URL = r'https://www.uvic.ca/calendar/future/undergrad/index.php#/courses'
CALENDAR_WIDGET_ID = r'__KUALI_TLP'
ACTION_TIMEOUT_SECONDS = 5


def main():
    '''Configures log level and scrapes the UVic course catalog'''
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)-8s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')

    scrape()


def scrape():
    '''Scrapes the UVic academic calendar using the given web driver

    The browser is periodically killed and replaced to reduce memory
    consumption.
    '''

    dept_links = run_browser_task(get_dept_links)
    LOGGER.info("Found %d department pages", len(dept_links))

    # Process department pages in groups.
    batch_size = 5  # Arbitrary choice
    dept_batches = partition_list(dept_links, batch_size)
    scrape_dept_batches(dept_batches)


def run_browser_task(run_task):
    '''Starts a new browser, runs the given task, and returns the result'''
    driver = driver_setup.get_webdriver()
    try:
        return run_task(driver)
    finally:
        driver.quit()


# Local objects cannot be pickled, so this must be defined as a top level function.
def _scrape_depts(links):
    '''A task to be executed by a worker process. Scrapes the given department links.
    '''
    # Create a connection to the database to be used by this process.
    # Note that psycopg2 connections cannot be shared between processes.
    conn = db.connect()
    task = partial(crawl_dept_pages, links, conn)
    run_browser_task(task)
    conn.close()


def scrape_dept_batches(batches):
    '''Uses a pool of workers to process the given batches of department links.

    Each batch is given to a worker and a separate browser is used for each
    call to prevent memory overages.
    '''
    num_workers = 2
    with Pool(num_workers) as pool:
        pool.map(_scrape_depts, batches)


def get_dept_links(browser):
    '''Return a list of all undergrad department page links'''
    browser.get(BASE_URL)
    return get_links_from_catalog(browser)


def partition_list(items, group_size):
    '''Return a list of sublists of the given list'''
    assert group_size > 0
    num_items = len(items)
    return [items[i:i+group_size] for i in range(0, num_items, group_size)]


def crawl_dept_pages(dept_links, db_connection, browser):
    '''Scrapes each department page given'''
    for link in dept_links:
        crawl_dept_page(link, browser, db_connection)


def crawl_dept_page(dept_link, browser, db_connection):
    '''Scrapes each course page accessible via the given department link'''
    browser.get(dept_link)

    LOGGER.info("Crawling department url: %s", format(dept_link))

    class_links = get_links_from_catalog(browser)
    crawl_course_pages(class_links, browser, db_connection)


def get_links_from_catalog(browser):
    '''Return a list of URLs from the catalog'''
    catalog_element = get_catalog_element(browser)
    return get_links_from_list_elements(catalog_element)


def get_catalog_element(browser, timeout=ACTION_TIMEOUT_SECONDS):
    '''Waits for the Kuali catalog to be rendered and returns a <div> containing it.'''
    wait = WebDriverWait(browser, timeout)
    search_key = (By.ID, CALENDAR_WIDGET_ID)
    element_found = EC.presence_of_element_located(search_key)
    return wait.until(element_found)


def get_links_from_list_elements(continer_element):
    '''Returns a link for each <li> which is a child of the given element'''
    lis = continer_element.find_elements_by_tag_name('li')
    return [get_link_from_list_item(li) for li in lis]


def get_link_from_list_item(li_element):
    '''Returns the href of the first <a> tag in the given <li> element.'''
    return li_element.find_element_by_tag_name('a').get_attribute('href')


def crawl_course_pages(links, browser, db_connection):
    '''Scrapes each course page

    Navigates to each link given, extracts the relevant information, and stores
    the findings to the database using the provided connection.
    '''
    for link in links:
        crawl_course_page(link, browser, db_connection)


def crawl_course_page(link, browser, db_connection):
    '''Scrapes the given course page and sends the results to the database'''
    get_and_wait_for_ajax_complete(link, browser)

    catalog_element = get_catalog_element(browser)
    listing = class_listing.get_from_web_element(catalog_element, link)
    send_to_database(listing, db_connection)


def get_and_wait_for_ajax_complete(link, browser):
    '''Gets the given page and returns once the AJAX requests have completed.

    This function assumes that the current page is part of the UVic academic
    calendar. It may fail if this is not the case. If you are navigating to
    a course page from some other page, a simple get() followed by
    get_catalog_element() should suffice.

    This is done by caching the value of the header element which title's the
    calendar <div> and waiting until it is updated to a different value.

    This may not guarantee that all AJAX requests are complete, but it should
    ensure that those that are replacing course information have finished.

    If the current page's url is the same as the provided link, then no action
    is taken.
    '''

    if browser.current_url == link:
        return

    header = get_catalog_element(browser).find_element_by_tag_name('h2')
    initial_text = header.text

    browser.get(link)
    wait = WebDriverWait(browser, ACTION_TIMEOUT_SECONDS)

    def get_header_element(browser):
        catalog = get_catalog_element(browser)
        return catalog.find_element_by_tag_name('h2')

    def header_updated(browser):
        return get_header_element(browser).text != initial_text

    wait.until(header_updated)


# Silently allow updates
INSERT_URL_QUERY_TEMPLATE = sql.SQL('''INSERT INTO course_urls 
VALUES (%s, %s) 
ON CONFLICT (course_code) 
DO UPDATE SET url=EXCLUDED.url
''')


def send_to_database(course, db_connection):
    '''Saves the data about the course to the Postgres database'''
    try: 
        cursor = db_connection.cursor() 
        cursor.execute(INSERT_URL_QUERY_TEMPLATE, (course.code, course.url))
        db_connection.commit()

    except Exception as error:
        LOGGER.error(error)
        db_connection.rollback()
    

if __name__ == '__main__':
    main()
