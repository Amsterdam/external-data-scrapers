#!/usr/bin/env bash

# Import ndw 

set -u   # crash on missing env variables
set -e   # stop on any error
set -x   # print what we are doing

export PYTHONPATH=/app/
DIR=`dirname "$0"`

dc() {
	docker-compose -p ndw-${ENVIRONMENT} -f $DIR/docker-compose.yml $*
}

trap 'dc kill ; dc down ; dc rm -f' EXIT

dc rm -f
dc pull
dc build

# create database tables if not exists.
if [ "$DROP" = "yes" ]
then
   dc run --rm importer python data_sources/ndw/models.py --drop

else
   dc run --rm importer python data_sources/ndw/models.py 
fi

if [ "$WFS" = "yes" ]
then
   # load current neighborhood data
   dc run --rm importer python load_wfs_postgres.py https://map.data.amsterdam.nl/maps/gebieden stadsdeel,buurt_simple 4326 --db externaldata
fi

# copy data into final table for serving to django
dc run --rm importer python data_sources/ndw/copy_to_model.py --ndw

dc down -v
