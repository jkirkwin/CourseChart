'''Entry point script for the web scraper.

Uses Selenium to scrape the UVic academic calendar for course relationships.
'''
import logging
import chromedriver_autoinstaller
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import class_listing

# TODO Explore where we can make savings by multithreading
# Can we examine each course page and send results to the database in its own thread?
# Python threads' implementation prevents parallelism, so we would need to use a 
# multiprocess model instead.
#
# Option:
#       This process creates a pool of workers which all read from a queue until either
#       it is marked as empty or they are killed.
#       The parent process (the one running this script currently), feeds into the queue
#       course URLs, department URLs, or even webelement objects to be parsed and converted
#       into tables in the database.
# Option:
#       This process creates a single child process and half of the course processing steps 
#       run on each one. This requires two browsers.

# Scraping constants
BASE_URL = r'https://www.uvic.ca/calendar/future/undergrad/index.php#/courses'
CALENDAR_WIDGET_ID = r'__KUALI_TLP'
ACTION_TIMEOUT_SECONDS = 5

LOGGER = logging.getLogger(__name__)


def main():
    '''Configures log level and scrapes the UVic course catalog'''
    logging.basicConfig(level="INFO")

    driver = get_webdriver()
    # No exceptions are currently being caught here. Instead of guessing ahead,
    # add handling cases as they are identified during testing.
    try:
        scrape(driver)
    finally:
        driver.quit()


def get_webdriver(headless=True):
    '''Creates and returns a selenium webdriver'''
    chromedriver_autoinstaller.install()

    opts = webdriver.ChromeOptions()
    opts.headless = headless
    chrome_driver = webdriver.Chrome(options=opts)

    # Allow for a small amount of latency for each action
    chrome_driver.implicitly_wait(1)

    return chrome_driver


def scrape(browser):
    '''Scrapes the UVic academic calendar using the given web driver'''
    browser.get(BASE_URL)

    dept_links = get_links_from_catalog(browser)
    LOGGER.info("Found %d department pages", len(dept_links))

    class_links = get_class_links(dept_links, browser)
    LOGGER.info("Found %d course pages", len(class_links))

    crawl_course_pages(class_links, browser)


def get_links_from_catalog(browser):
    '''Return a list of URLs from the catalog'''
    catalog_element = wait_for_catalog_load(browser)
    return get_links_from_list_elements(catalog_element)


def wait_for_catalog_load(browser, timeout=ACTION_TIMEOUT_SECONDS):
    '''Waits for the Kuali catalog to be rendered

    Waits until either the catalog element is rendered or the timeout is exceeded.
    Returns the catalog element if it renders in time.
    '''
    wait = WebDriverWait(browser, timeout)
    search_key = (By.ID, CALENDAR_WIDGET_ID)
    condition = EC.presence_of_element_located(search_key)
    return wait.until(condition)


def get_links_from_list_elements(continer_element):
    '''Returns a link for each <li> which is a child of the given element'''
    lis = continer_element.find_elements_by_tag_name('li')
    return [get_link_from_list_item(li) for li in lis][:20] # TODO Limiting output


def get_link_from_list_item(li_element):
    '''Returns the href of the first <a> tag in the given <li> element.'''
    return li_element.find_element_by_tag_name('a').get_attribute('href')


def get_class_links(dept_links, browser):
    '''Returns links to each class reachable from the given deparmental URLs'''
    result = []
    for link in dept_links:
        browser.get(link)
        class_links = get_links_from_catalog(browser)
        result.extend(class_links)
    return result


def crawl_course_pages(links, browser):
    '''Scrapes each course page

    Navigates to each link given and extracts the relevant information.
    The findings are sent to the database.
    '''
    for link in links:
        browser.get(link)
        catalog_element = wait_for_catalog_load(browser)

        listing = class_listing.get_from_web_element(catalog_element)
        send_to_database(listing)


def send_to_database(course):
    ''''''
    # TODO
    pass


if __name__ == '__main__':
    main()
