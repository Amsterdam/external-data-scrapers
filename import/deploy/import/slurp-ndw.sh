#!/usr/bin/env bash

# Import ndw 

set -u   # crash on missing env variables
set -e   # stop on any error
set -x   # print what we are doing

export PYTHONPATH=/app/
DIR=`dirname "$0"`

dc() {
	docker-compose -p ndw-slurp-${ENVIRONMENT} -f $DIR/docker-compose.yml $*
}

trap 'dc kill ; dc down ; dc rm -f' EXIT

# remove extra network
for i in $(docker network ls | awk '/ndw-slurp-acceptance_default/ {print $1}'); do docker network rm $i; done

dc rm -f
dc pull
dc build

# Slurp ovfiets
dc run --rm importer python data_sources/ndw/slurp.py traveltime
dc run --rm importer python data_sources/ndw/slurp.py trafficspeed

dc down -v
