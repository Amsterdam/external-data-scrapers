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
   dc run --rm importer python data_sources/ndw/models.py --drop_daily

else
   dc run --rm importer python data_sources/ndw/models.py
fi

# copy data into final table for serving to django
dc run --rm importer python data_sources/ndw/summarize.py traveltime
dc run --rm importer python data_sources/ndw/summarize.py trafficspeed

dc down -v
