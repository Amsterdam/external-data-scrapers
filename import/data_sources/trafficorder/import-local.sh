#!/bin/bash

set -xue

python data_sources/trafficorder/models.py

python load_wfs_postgres.py https://map.data.amsterdam.nl/maps/gebieden stadsdeel,buurt_simple 4326 --db externaldata

python data_sources/trafficorder/slurp.py --year 2019

python data_sources/trafficorder/copy_to_model.py 
python data_sources/trafficorder/copy_to_model.py --link_areas
