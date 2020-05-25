# CourseChart
A visual tool to show the relationships between courses at UVic.

[![Master Branch Build Status](https://travis-ci.com/jkirkwin/CourseChart.svg?branch=master)](https://travis-ci.com/jkirkwin/CourseChart)

## Project structure
The root directory contains the NodeJS app for the website. 

## Github/git
`master` branch is protected and requires pull requests to be updated.

Name dev branches as `dev/<contributor name>/<feature>`.

## CI and Deploymet
All branches are automatically built by [Travis](travis-ci.com). Heroku monitors `master` and automatically deploys if the CI build succeeds.

We are hosting on travis-ci.__com__, not travis-ci.__org__. If you are using Travis' CLI (you can get it with `gem install travis`), then you will need to add the `--pro` or `--com` flag to each command as it defaults to the .org server.

## Outstanding
* Contributors added to Heroku app
* DB setup 
* DB accessibile from Node app
* Scraper template created and CI/CD running
* Project structure decided and updated
* JSLint setup (or alternative) for CI