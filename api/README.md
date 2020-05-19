Imported data
=============

* [OV](./src/apps/ov/README.md)
* [ovfiets](./src/apps/ovfiets/README.md)
* [parkeergarages](./src/apps/parkeergarages/README.md)


## apps

### base
neighbourhood/stadsdeel models and importer.

### health
Internal use only for the load balancer

### objectstore
Archiver of raw data tables to the object store. More info [here](./src/apps/ov/README.md#archiving-data)

### ndw
The api for ndw data, imported in the import directory

### OV
OV data subscriber

### ovfiets
Ovfiets importer and api. Uses [datapunt-django-snapshot](https://github.com/Amsterdam/datapunt-django-snapshot)

### parkeergarages
Parkeergarages importer and api. Uses [datapunt-django-snapshot](https://github.com/Amsterdam/datapunt-django-snapshot)

## Deploy scripts

Under `api/deploy` there are multiple directories for different scripts run by jenkins

- `api/deploy/archive` Archive script for raw models refer to [here](./src/apps/ov/README.md#archiving-data)
- `api/deploy/import` All data sources import script
- `api/deploy/ovlookup_data` Scripts related to OV data source. Explanation [here](./src/apps/ov/README.md)
- `api/deploy/summarize` Scripts that summarizes the data imported daily for ovfiets and parkeergarages

## Tables currently archived in the objectstore
- OvRaw(ov_ovraw)
- OVFietsSnapshot(ovfiets_raw)
- ParkingLocationSnapshot(parkinglocation_raw)
- GuidanceSignSnapshot(guidancesign_raw)
