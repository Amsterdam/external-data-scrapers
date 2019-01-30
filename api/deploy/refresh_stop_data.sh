#!/usr/bin/env bash

set -u   # crash on missing env variables
set -e   # stop on any error
set -x   # print what we are doing

source /deploy/docker-wait.sh
# cleanup files van previous failed runs?
rm -f stops.txt
rm -f gtfs-nl.zip
wget http://gtfs.ovapi.nl/nl/gtfs-nl.zip
unzip -j gtfs-nl.zip stops.txt -d .
python /app/manage.py loadstops stops.txt
rm -f stops.txt
rm -f gtfs-nl.zip
