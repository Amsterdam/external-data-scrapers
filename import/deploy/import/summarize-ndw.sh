#!/usr/bin/env bash

# Import ndw

set -u   # crash on missing env variables
set -e   # stop on any error
set -x   # print what we are doing

export PYTHONPATH=/app/
DIR=`dirname "$0"`

dc() {
	docker-compose -p ndw-summarize-${ENVIRONMENT} -f $DIR/docker-compose.yml $*
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

psql -U $DATABASE_OVERRIDE_USER -h $DATABASE_OVERRIDE_HOST $DATABASE_OVERRIDE_NAME < data_sources/ndw/insert_daily.sql

dc down -v
