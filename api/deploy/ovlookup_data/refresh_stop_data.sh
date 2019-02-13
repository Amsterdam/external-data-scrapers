#!/usr/bin/env bash

set -u   # crash on missing env variables
set -e   # stop on any error
set -x   # print what we are doing
DIR=`pwd`

#source /deploy/docker-wait.sh
# cleanup files van previous failed runs?
rm -f stops.txt trips.txt shapes.txt gtfs-nl.zip
wget http://gtfs.ovapi.nl/nl/gtfs-nl.zip
unzip -j gtfs-nl.zip stops.txt trips.txt shapes.txt -d .
psql -U $DATABASE_USER -h $DATABASE_HOST $DATABASE_NAME < /deploy/ovlookup_data/refresh.sql
rm -f stops.txt trips.txt shapes.txt gtfs-nl.zip
