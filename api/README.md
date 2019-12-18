External data scrapers
======================

## Manual Installation

### Run database in docker
```
docker-compose up database
```

### Install dependencies (django is separate to keep it up to date with security fixes)
```
make install_requirements
```
OR
```
pip -r requirements.txt -r requirements-django.txt
```

### Create the tables
```
python src/manage.py migrate
```

### Run the server

```
python src/manage.py runserver
```
