#!/bin/sh

set -e
set -u
set -x

DIR="$(dirname $0)"

dc() {
   docker-compose -p external-data-scrapers-test -f ${DIR}/docker-compose.yml $*
}

dc stop
dc rm --force
dc down
dc pull
dc build

dc up -d database

dc run --rm importer /app/deploy/docker-wait.sh

dc run --rm importer tox -- --create-db


dc stop
dc rm --force
dc down
