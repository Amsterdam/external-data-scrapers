#!/usr/bin/env bash

# Import ndw

set -u   # crash on missing env variables
set -e   # stop on any error
set -x   # print what we are doing

export PYTHONPATH=/app/
DIR=`dirname "$0"`

dc() {
	docker-compose -p ndw-verkeersmanagement-daily-${ENVIRONMENT} -f $DIR/docker-compose.yml $*
}

trap 'dc kill ; dc down ; dc rm -f' EXIT

dc rm -f
dc pull
dc build

if [ "$INSERT" = "yes" ]
then
    dc run --rm importer psql -U $DATABASE_OVERRIDE_USER -h $DATABASE_OVERRIDE_HOST -d $DATABASE_OVERRIDE_NAME -v ON_ERROR_STOP=1 /deploy/verkeersmanagement/create_tables_and_view.sql
    dc run --rm importer psql -U $DATABASE_OVERRIDE_USER -h $DATABASE_OVERRIDE_HOST -d $DATABASE_OVERRIDE_NAME -v ON_ERROR_STOP=1 /deploy/verkeersmanagement/insert_hulptabel.sql
fi

dc run --rm importer psql -U $DATABASE_OVERRIDE_USER -h $DATABASE_OVERRIDE_HOST -d $DATABASE_OVERRIDE_NAME -v ON_ERROR_STOP=1 /deploy/verkeersmanagement/insert_daily_netwerkprestatie.sql

dc down -v
