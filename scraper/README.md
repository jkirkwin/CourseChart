# Web Scraper

The main script for the scraper utility is `scraper.py`. It uses Selenium and ChromeDriver to navigate to each course page in the uvic academic calendar, scrape data and metadata, and store those data in the postgres database.

## Local development environment

Chrome and [ChromeDriver](https://chromedriver.chromium.org/downloads) are both needed for local development, and you'll need the correct version of chromedriver for your version of Chrome. See `driver_setup.py` for a more in depth description of how the driver must be configured.

To connect the scraper to a database, set the `DATABASE_URL` environment variable.
