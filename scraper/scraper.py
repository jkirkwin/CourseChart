'''Entry point script for the web scraper.

Uses Selenium to scrape the UVic academic calendar for course relationships.
'''

import logging
from functools import partial
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import driver_setup
import class_listing

# TODO Refactor to prevent memory errors on heroku - recycle browser after n requests

# TODO Explore where we can make savings by multiprocessing
# Use pools of processes for scraping tasks?
# Use separate processes to push data into the db(s)?

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
    '''Scrapes the UVic academic calendar using the given web driver'''

    dept_links = run_browser_task(get_dept_links)
    LOGGER.info("Found %d department pages", len(dept_links))

    for link in dept_links:
        task = partial(crawl_dept_page, link)
        run_browser_task(task)


def run_browser_task(run_task):
    '''Starts a new browser, runs the given task, and returns the result'''
    driver = driver_setup.get_webdriver()
    try:
        return run_task(driver)
    finally:
        driver.quit()


def get_dept_links(browser):
    '''Return a list of all undergrad department page links'''
    browser.get(BASE_URL)
    return get_links_from_catalog(browser)


def crawl_dept_page(dept_link, browser):
    '''Scrapes each course page accessible via the given department link'''
    browser.get(dept_link)
    class_links = get_links_from_catalog(browser)
    crawl_course_pages(class_links, browser)


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


def crawl_course_pages(links, browser):
    '''Scrapes each course page

    Navigates to each link given and extracts the relevant information.
    The findings are sent to the database.
    '''
    for link in links:
        crawl_course_page(link, browser)


def crawl_course_page(link, browser):
    '''Scrapes the given course page and sends the results to the database'''
    get_and_wait_for_ajax_complete(link, browser)

    catalog_element = get_catalog_element(browser)
    listing = class_listing.get_from_web_element(catalog_element)
    send_to_database(listing)


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


def send_to_database(course):
    '''Saves the data about the course to the Postgres database'''
    # TODO Implement
    print(course.code + " - " + course.name)

if __name__ == '__main__':
    main()
