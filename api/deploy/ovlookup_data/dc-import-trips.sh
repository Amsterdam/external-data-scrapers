#!/usr/bin/env bash

# Import ndw 

set -u   # crash on missing env variables
set -e   # stop on any error
set -x   # print what we are doing

export PYTHONPATH=/app/
DIR=`dirname "$0"`

dc() {
	docker-compose -p ov-api-jobs-${ENVIRONMENT} -f $DIR/docker-compose.yml $*
}

trap 'dc kill ; dc down ; dc rm -f' EXIT

dc rm -f
dc pull
dc build

dc run --rm api python manage.py kv6partition
dc run --rm api /deploy/ovlookup_data/refresh_stop_data.sh
dc run --rm api /deploy/archive/archive-tables.sh

dc down -v
