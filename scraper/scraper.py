'''Entry point script for the web scraper.

Uses Selenium to scrape the UVic academic calendar for course relationships.
'''
import chromedriver_autoinstaller
import selenium.webdriver


URL = r'https://www.uvic.ca/calendar/future/undergrad/index.php#/courses'


def getWebdriver(headless=True):
    chromedriver_autoinstaller.install()
    opts = selenium.webdriver.ChromeOptions()
    driver = selenium.webdriver.Chrome(options=opts)
    return driver


if __name__ == '__main__':      
    try: 
        driver = getWebdriver()
        driver.get(URL)
        driver.close()
    except Exception as e:
        print(repr(e))
