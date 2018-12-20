#!/usr/bin/env bash

# Import ovfiets 

set -u   # crash on missing env variables
set -e   # stop on any error
set -x   # print what we are doing

export PYTHONPATH=/app/
DIR=`dirname "$0"`

dc() {
	docker-compose -p ovfiets-${ENVIRONMENT} -f $DIR/docker-compose.yml $*
}

trap 'dc kill ; dc down ; dc rm -f' EXIT

dc rm -f
dc pull
dc build

# Slurp ovfiets
dc run --rm importer python data_sources/ovfiets/slurp.py

dc down -v
