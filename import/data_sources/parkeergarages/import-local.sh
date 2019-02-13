#!/bin/bash

set -xue

python data_sources/parkeergarages/models.py

python load_wfs_postgres.py https://map.data.amsterdam.nl/maps/gebieden stadsdeel,buurt_simple 4326 --db externaldata

for i in {1..5};
do python data_sources/parkeergarages/slurp.py parking_location && python data_sources/parkeergarages/slurp.py guidance_sign;
done

python data_sources/parkeergarages/copy_to_model.py parking_location
python data_sources/parkeergarages/copy_to_model.py guidance_sign
python data_sources/parkeergarages/copy_to_model.py parking_location --link_areas
python data_sources/parkeergarages/copy_to_model.py guidance_sign --link_areas
