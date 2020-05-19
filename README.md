# External data scrapers

External data scrapers is a REST api that contains data scraped from different data sources.
The api is intended to be used by different projects without the need for each one to create their
own scraper. For this reason, the name is generic.

## Structure

# [Api directory](./api/README.md)
Django project with Django rest framework. Exposes the data scraped. Contains
data scrapers for the following data sources. 

- OvFiets
- Parkeergarages
- OV 


# [Import directory](./import/README.md)
Python project with slurp (retrieve from data source) and copy_to_model (cleanup and copy to new table) scripts. Uses sql alchemy for the database models.

- NDW (Traveltime, Trafficspeed)
- VerkeerBesluiten (TrafficOrder)

(NDW: Nationale Databank Wegverkeersgegevens)


# Shared models
All data sources were only scraped in the `import` directory and the models
were shared with the `api` directory to be exposed by django. Most data sources
have been migrated to be scraped using django in the `api` directory except for the `ndw`
data source due to time constrains.

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

### Populate stadsdeel/Neighbourhood models
Most datasources are augmented with the stadsdeel and buurt_code 
based on the bag model.

Each directory has it's own way of importing the bag model

### API directory stadsdeel
```
docker-compose run --rm api ./manage.py import_areas
```

#### Import directory stadsdeel
```
docker-compose run --rm import python load_wfs_postgres.py https://map.data.amsterdam.nl/maps/gebieden stadsdeel,buurt_simple 4326 --db externaldata
```

### Import local data

#### API directory

Scrape raw data
```
docker-compose run --rm api ./manage.py scrape_ovfiets
```
Import scraped data
```
docker-compose run --rm api ./manage.py import_ovfiets
```

#### Import directory
```
docker-compose run --rm import ./data_sources/ndw/import-local.sh
```

### Running the server

```
docker-compose up api
```

Server should be available here  `http://localhost:8001/externaldata`
