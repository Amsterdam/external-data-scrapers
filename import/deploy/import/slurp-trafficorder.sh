#!/usr/bin/env bash

# Import trafficorder 

set -u   # crash on missing env variables
set -e   # stop on any error
set -x   # print what we are doing

export PYTHONPATH=/app/
DIR=`dirname "$0"`

dc() {
	docker-compose -p trafficorder-slurp-${ENVIRONMENT} -f $DIR/docker-compose.yml $*
}

trap 'dc kill ; dc down ; dc rm -f' EXIT

dc rm -f
dc pull
dc build

if [ "$MONTHLY" = "yes"]
then
    dc run --rm importer python data_sources/trafficorder/slurp.py --monthly
else
    dc run --rm importer python data_sources/trafficorder/slurp.py --year $year
fi

dc down -v
