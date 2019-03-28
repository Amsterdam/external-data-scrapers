#!/usr/bin/env bash

# Import wifiinfo 

set -u   # crash on missing env variables
set -e   # stop on any error
set -x   # print what we are doing

export PYTHONPATH=/app/
DIR=`dirname "$0"`

dc() {
	docker-compose -p wifiinfo-copy-${ENVIRONMENT} -f $DIR/docker-compose.yml $*
}

trap 'dc kill ; dc down ; dc rm -f' EXIT

dc rm -f
dc pull
dc build

# create database tables if not exists.
if [ "$DROP" = "yes" ]
then
   dc run --rm importer python data_sources/wifiinfo/models.py --drop

else
   dc run --rm importer python data_sources/wifiinfo/models.py 
fi


dc run --rm importer python data_sources/wifiinfo/copy_to_model.py

dc down -v


