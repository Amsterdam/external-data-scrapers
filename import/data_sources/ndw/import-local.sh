#!/bin/bash

set -xue

python data_sources/ndw/models.py

for i in {1..5};
do python data_sources/ndw/slurp.py --ndw && python data_sources/ndw/slurp.py --thirdparty;
done

export IMPORT_LIMIT=10
python data_sources/ndw/copy_to_model.py --ndw
unset IMPORT_LIMIT
python data_sources/ndw/copy_to_model.py --thirdparty
