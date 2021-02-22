# CourseChart
A visual tool to show the relationships between courses at UVic.

[![Master Branch Build Status](https://travis-ci.com/jkirkwin/CourseChart.svg?branch=master)](https://travis-ci.com/jkirkwin/CourseChart)

## Project structure
`/server/` contains the NodeJS webserver and associated files. The root directory contains the related `package.json` and `package-lock.json`. Running `npm install` from inside the `server` directory will update the root-level package files. 

`/scraper/` contains the Python web scraper. A root-level `requirements.txt` file is used to signal to the Heroku 'Buildpack' system that this is a Python application.

## Github/git
`master` branch is protected and requires pull requests to be updated.

Name dev branches as `dev/<contributor name>/<feature>`.

## CI / CD

### Travis (CI)
All branches are automatically built by [Travis](travis-ci.com). 

We are hosting on travis-ci.__com__, not travis-ci.__org__. If you are using Travis' CLI (you can get it with `gem install travis`), then you will need to add the `--pro` or `--com` flag to each command as it defaults to the .org server.

You can manually trigger a Travis build through the website. 

See `.travis.yml` for configuration.

### Heroku (Deployment)
[Heroku](https://dashboard.heroku.com/apps/coursechart) monitors `master` and automatically deploys it each time a pull request is merged if and only if the CI build succeeds. 

Dev branches can be deployed manually on Heroku via the web interface, or locally using `heroku local` (requires the Heroku CLI).

See `Procfile` and Heroku website for configuration.

You can run `heroku run scrape -a coursechart` to manually run the Python scraper.

## Database

The web scraper saves the course data in a postgres database hosted via Heroku ([documentation](https://devcenter.heroku.com/articles/heroku-postgresql)). 
