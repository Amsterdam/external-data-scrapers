Imported data
=============

* OvFiets

## About OvFiets

- Scraper for http://fiets.openov.nl/ the status of available rental bikes at train stations

- Raw data is saved as is for history persistency
- Raw data is cleaned and copied to another model.
- Django REST api views the cleaned data.
- Django model needs to be in sync with the imported model

## Instructions OvFiets

### set python path

```
export PYTHONPATH=.
```

### Create models

```
python data_sources/ovfiets/models.py
```


### load wfs data (neighbourhoods)

```
python load_wfs_postgres.py https://map.data.amsterdam.nl/maps/gebieden stadsdeel 4326 --db external-data-scrapers
```

### Import api instance
```
python data_sources/ovfiets/slurp.py
```

### cleanup and copy to model
```
python data_sources/ovfiets/copy_to_model.py
```

### Link neighbourhoods
```
python data_sources/ovfiets/copy_to_model.py --link_areas
```


## Tests
```
tox
```
