Imported data
=============

* [NDW](data_sources/ndw/README.md)
* [Verkeerbesluiten](data_sources/trafficorder/README.md)


## Run tests
```
tox
```

## Database configuration

The `config.ini` file contains the local docker and test database config. If an external database is to be used, add the environment variable `OVERRIDE_DATABASE` and the database config (found in settings.py)
In some cases the scraped data doesn't need to be persistent and can be rebuilt everyday then restored to the production db. In other cases like `Ovfiets` the database is long running and persistent it is necessary to write to the production db directly.


## Scripts

The following scripts (mostly) apply to all data sources, with some requiring specific arguments.

### Move to import root
```
cd ..
```
### Set python path

```
export PYTHONPATH=.
```

### Load wfs data (neighbourhoods)

```
python load_wfs_postgres.py https://map.data.amsterdam.nl/maps/gebieden stadsdeel,buurt_simple 4326 --db externaldata
```

### Create models script

```
python data_sources/{data_source}/models.py  {--drop}
```

### Import api instance
```
python data_sources/{data_source}/slurp.py {args}
```

### Cleanup and copy to model
```
python data_sources/{data_source}/copy_to_model.py {args}
```

### Link neighbourhoods (Not applicable for all data sources)
```
python data_sources/{data_source}/copy_to_model.py {args} --link_areas
```
