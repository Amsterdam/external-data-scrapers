#!/usr/bin/env bash

set -u   # crash on missing env variables
set -e   # stop on any error

# start zmq subscribers and run uwsgi
cd /app/
exec python manage.py kv6sub &
exec uwsgi
