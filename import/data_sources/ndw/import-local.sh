#!/bin/bash

set -xue

python data_sources/ndw/models.py

python data_sources/ndw/slurp.py traveltime 
python data_sources/ndw/slurp.py trafficspeed

export IMPORT_LIMIT=5
python data_sources/ndw/copy_to_model.py traveltime 
python data_sources/ndw/copy_to_model.py trafficspeed 
