# External data scrapers

External data scrapers is a REST api that contains data scraped from different data sources.
The api is intended to be used by different projects without the need for each one to create their
own scraper. For this reason, the name is generic.

## Structure

# api directory 
Django project with Django rest framework. Exposes the data scraped.

# import 
Python project with slurp (retrieve from data source) and copy_to_model (cleanup and copy to new table) scripts. Uses sql alchemy for the database models.

## Currently Scraped Data sources

- OvFiets
- Parkeergarages
- NDW (Traveltime)
- VerkeerBesluiten (TrafficOrder)

(NDW: Nationale Databank Wegverkeersgegevens)

## Running using Docker

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

### Migrating the django database

```
docker-compose run api ./manage.py migrate
```

### Import local data

```
docker-compose run --rm import ./data_sources/{data_source}/import-local.sh
```

### Running the server

```
docker-compose up
```

Server should be available here  `http://localhost:8001/public`


## Makefile (For local development)

The `api` and `import` directories contain a Makefile that contains the following commands

```
make requirements.txt
```

Installs all packages added in requirements-root.txt and updates the adds/updates them in requirements.txt

```
pyclean
```

Removes all `.pyc ` files in the directory

```
make isort
```

Runs isort to sort the imports in the repo
