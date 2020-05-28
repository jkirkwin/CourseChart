'''Entry point script for the web scraper.

Uses Selenium to scrape the UVic academic calendar for course relationships.
'''
import logging
import chromedriver_autoinstaller
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# TODO Explore where we can make savings by multithreading
# Can we examine each course page and send results to the database in its own thread?

# Scraping constants
BASE_URL = r'https://www.uvic.ca/calendar/future/undergrad/index.php#/courses'
DEPT_COURSE_LIST_URL_PREFIX = BASE_URL + r'?group='
CALENDAR_WIDGET_ID = r'__KUALI_TLP'
ACTION_TIMEOUT_SECONDS = 5

LOGGER = logging.getLogger(__name__)

def get_webdriver(headless=True):
    '''Creates and returns a selenium webdriver'''
    chromedriver_autoinstaller.install()

    opts = webdriver.ChromeOptions()
    opts.headless = headless
    chrome_driver = webdriver.Chrome(options=opts)

    # Allow for a small amount of latency for each action
    chrome_driver.implicitly_wait(1)

    return chrome_driver


def wait_for_catalog_load(browser, timeout=ACTION_TIMEOUT_SECONDS):
    '''Waits for the Kuali catalog to be rendered

    Waits until either the catalog element is rendered or the timeout is exceeded.
    Returns the catalog element if it renders in time.
    '''
    wait = WebDriverWait(browser, timeout)
    search_key = (By.ID, CALENDAR_WIDGET_ID)
    condition = EC.presence_of_element_located(search_key)
    return wait.until(condition)


# Utility for debugging
# TODO delete
def show_list(items):
    '''Prints each element in the list on a new line'''
    for item in items:
        print(item)


def get_dept_keys(lis):
    '''Returns the key for each department in the given list of <li> elements

    Each <li> corresponds to a single department. The department key is
    extracted for each one.
    Department keys are of the form "<Full Name of Department> (<Department Code>)".
    For example, the key for the Computer Science department is
                "Computer Science (CSC)"
    '''
    get_dept_key = lambda li: li.find_element_by_tag_name('div').get_attribute('name')
    return [get_dept_key(li) for li in lis]


def get_dept_page_link(dept_key):
    '''Returns the URL for the given deparment's undergraduate course page'''
    return DEPT_COURSE_LIST_URL_PREFIX + dept_key


def get_dept_page_links(lis):
    '''Returns the URL for each department in the given list of <li> elements'''
    dept_keys = get_dept_keys(lis)
    return [get_dept_page_link(k) for k in dept_keys]


def get_class_page_link(li_element):
    '''Returns the URL for the given class list element'''
    return li_element.find_element_by_tag_name('a').get_attribute('href')


def get_class_page_links(lis):
    '''Returns the URL for eah class in the given list of <li> elementes'''
    return [get_class_page_link(li) for li in lis]


def get_all_class_links(dept_links, browser):
    '''Returns links to each class reachable from the given deparmental URLs'''
    result = []
    for link in dept_links:
        browser.get(link)
        catalog_element = wait_for_catalog_load(browser)
        list_items = catalog_element.find_elements_by_tag_name('li')
        class_links = get_class_page_links(list_items)
        result.extend(class_links)
    return result


def crawl_course_pages(links, browser):
    '''Scrapes each course page

    Navigates to each link given and extracts the relevant information. 
    The findings are sent to the database.
    '''
    LOGGER.info("Crawling %d course pages", len(links))
    
    # TODO visit each page and extract information


def crawl_dept_pages(dept_links, browser):
    '''Scrapes each of the given department pages'''
    LOGGER.info("Crawling %d department pages", len(dept_links))
    
    links = get_all_class_links(dept_links, browser)
    crawl_course_pages(links, browser)


def scrape(browser):
    '''Scrapes the UVic academic calendar using the given web driver'''
    browser.get(BASE_URL)
    catalog_element = wait_for_catalog_load(browser)
    list_items = catalog_element.find_elements_by_tag_name('li')
    dept_links = get_dept_page_links(list_items)
    crawl_dept_pages(dept_links, browser)


if __name__ == '__main__':
    logging.basicConfig(level="INFO")

    driver = get_webdriver()

    # No exceptions are currently being caught here. Instead of guessing ahead,
    # add handling cases as they are identified during testing.
    try:
        scrape(driver)
    finally:
        driver.quit()
