#!/bin/bash

set -xue

python data_sources/ndw/models.py

for i in {1..5};
do python data_sources/ndw/slurp.py;
done

export IMPORT_LIMIT=10
python data_sources/ndw/copy_to_model.py 
