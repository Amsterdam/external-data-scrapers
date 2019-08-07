#!/usr/bin/env bash

# Import boat tracking 

set -u   # crash on missing env variables
set -e   # stop on any error
set -x   # print what we are doing

export PYTHONPATH=/app/
DIR=`dirname "$0"`

dc() {
	docker-compose -p import-boat_tracking-${ENVIRONMENT} -f $DIR/docker-compose.yml $*
}

trap 'dc kill ; dc down ; dc rm -f' EXIT

dc rm -f
dc pull
dc build

dc run --rm api python manage.py import_boat_tracking

dc down -v

