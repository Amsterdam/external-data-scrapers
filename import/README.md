Imported data
=============

* [OvFiets](data_sources/ovfiets/README.md)
* [Parkeergarages](data_sources/parkeergarages/README.md)

## Run tests
```
tox
```

## Database configuration

The `config.ini` file contains the local docker and test database config. If an external database is to be used, add the environment variable `OVERRIDE_DATABASE` and the database config (found in settings.py)
In some cases the scraped data doesn't need to be persistent and can be rebuilt everyday then restored to the production db. In other cases like `Ovfiets` the database is long running and persistent it is necessary to write to the production db directly.