#!/usr/bin/env bash

# Import parkeergarages 

set -u   # crash on missing env variables
set -e   # stop on any error
set -x   # print what we are doing

export PYTHONPATH=/app/
DIR=`dirname "$0"`

dc() {
	docker-compose -p parkeergarages-${ENVIRONMENT} -f $DIR/docker-compose.yml $*
}

trap 'dc kill ; dc down ; dc rm -f' EXIT

dc rm -f
dc pull
dc build

# Slurp endpoints
dc run --rm importer python data_sources/parkeergarages/slurp.py parking_location
dc run --rm importer python data_sources/parkeergarages/slurp.py guidance_sign

dc down -v
