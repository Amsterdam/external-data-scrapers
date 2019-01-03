External data scrapers
======================

## Manual Installation

### Run database in docker
```
cd ..
docker-compose up database
```

### Create the tables
```
python src/manage.py migrate
```

### Run the server

```
python src/manage.py runserver
```