#!/bin/bash

set -xue

python data_sources/ndw/models.py

for i in {1..5};
do python data_sources/ndw/slurp.py traveltime && python data_sources/ndw/slurp.py trafficspeed;
done

export IMPORT_LIMIT=5
python data_sources/ndw/copy_to_model.py traveltime --exclude_areas
python data_sources/ndw/copy_to_model.py trafficspeed --exclude_areas
