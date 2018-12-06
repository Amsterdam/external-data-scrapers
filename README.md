# External data scrapers

This repo contains Scrapers that are intended to be used by several projects.

The import directory Contains the Scrapers

The api directory contains the REST api 

## Currently Scraped APIs

- OvFiets


## Running using Docker for local development

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

### Migrating the database
```
docker-compose run api ./manage.py migrate
```

### Running the server
```
docker-compose up
```

Server should be available here  `http://localhost:8001/public`



## Makefile

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