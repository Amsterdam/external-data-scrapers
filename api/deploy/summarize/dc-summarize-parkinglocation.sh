#!/usr/bin/env bash

set -u   # crash on missing env variables
set -e   # stop on any error
set -x   # print what we are doing

export pythonpath=/app/
dir=`dirname "$0"`

dc() {
	docker-compose -p parkinglocation-summarize-daily-${ENVIRONMENT} -f $dir/docker-compose.yml $*
}

trap 'dc kill ; dc down ; dc rm -f' exit

dc rm -f
dc pull
dc build

dc run --rm api psql -U $DATABASE_USER -h $DATABASE_HOST $DATABASE_NAME -v ON_ERROR_STOP=1 -f apps/parkeergarages/sql/summarize_daily.sql

dc down -v
