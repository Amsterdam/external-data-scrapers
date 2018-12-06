# External data scrapers

This repo contains Scrapers that are intended to be used by several projects.

The import directory Contains the Scrapers

The api directory contains the REST api 

## Currently Scraped APIs

- OvFiets


## Running using Docker for l ocal development

### Prerequisites
* git
* Docker

### Cloning the repo

```
git clone https://github.com/Amsterdam/external-data-scrapers.git 
```
### Building the Docker images
Pull the relevant images and build the services:
```
docker-compose pull
docker-compose build
```
### Running the test suite and style checks
Start the Postgres database and run the test
suite for both the api and import modules


```
docker-compose up -d database
docker-compose run --rm api tox 
docker-compose run --rm import tox 
```