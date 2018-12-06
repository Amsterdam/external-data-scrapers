#!/bin/bash

set -xue

python data_sources/ovfiets/models.py

python load_wfs_postgres.py https://map.data.amsterdam.nl/maps/gebieden stadsdeel 4326 --db externaldata

for i in {1..5};
do python data_sources/ovfiets/slurp.py;
done

python data_sources/ovfiets/copy_to_model.py
python data_sources/ovfiets/copy_to_model.py --link_areas
