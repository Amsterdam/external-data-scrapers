External data scrapers
======================

## Manual Installation

### Run database in docker
```
cd ..
docker-compose up database
```

### Create the tables
Currently there is not table to be migrated because ovfiets model is unmanaged by django, it is managed by sqlalchemy, but could be relevant in the future

```
python src/manage.py migrate
```

### Run the server

```
python src/manage.py runserver
```