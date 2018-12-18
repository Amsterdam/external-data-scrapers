#!/usr/bin/env bash

# Import ovfiets 

set -u   # crash on missing env variables
set -e   # stop on any error
set -x   # print what we are doing

export PYTHONPATH=/app/
DIR=`dirname "$0"`

dc() {
	docker-compose -p ovfiets-${ENVIRONMENT} -f $DIR/docker-compose-ovfiets.yml $*
}

trap 'dc kill ; dc down ; dc rm -f' EXIT

dc rm -f
dc pull
dc build

# create database tables if not exists.
if [ "$DROP" = "yes" ]
then
   dc run --rm importer python data_sources/ovfiets/models.py --drop

else
   dc run --rm importer python data_sources/ovfiets/models.py
fi

if [ "$WFS" = "yes" ]
then
   # load current neighborhood data
   dc run --rm importer python load_wfs_postgres.py https://map.data.amsterdam.nl/maps/gebieden stadsdeel 4326 --db externaldata
fi

# Slurp ovfiets
dc run --rm importer python data_sources/ovfiets/slurp.py

# copy data into final table for serving to django
dc run --rm importer python data_sources/ovfiets/copy_to_model.py

# link areas to stations
dc run --rm importer python data_sources/ovfiets/copy_to_model.py --link_areas

dc down -v
