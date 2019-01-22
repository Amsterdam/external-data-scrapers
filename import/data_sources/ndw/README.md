## About NDW (Nationale Databank Wegverkeersgegevens)
NDW is a datasource that contains traffic data (for more info check: https://www.ndw.nu/en/)
We are currently scraping traveltime data. The duration cars took to go through specific routes around the Netherlands. 

There are two sources scraped for the same data:

- http://opendata.ndw.nu/traveltime.xml.gz The official NDW api.
- http://web.redant.net/~amsterdam/ndw/data/reistijdenAmsterdam.geojson  Thirdparty source with extra information

The following applies to both sources:
- Raw data is saved as is for history persistency
- Raw data is cleaned and copied to another model.
- Django REST api views the cleaned data.
- Django model needs to be in sync with the imported model

The third party data source is scraped/imported because historical data already exists for it and it is a ready made geojson with coordinated.


## Instructions OvFiets

### Move to import root
```
cd ..
```
### Set python path

```
export PYTHONPATH=.
```

### Create models

```
python data_sources/ndw/models.py --ndw
python data_sources/ndw/models.py --thirdparty
```

### Import api instance
```
python data_sources/ndw/slurp.py --ndw
python data_sources/ndw/slurp.py --thirdparty
```

### Cleanup and copy to model
```
python data_sources/ndw/copy_to_model.py --ndw
python data_sources/ndw/copy_to_model.py --thirdparty
```