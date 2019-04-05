#!/usr/bin/env bash

set -u   # crash on missing env variables
set -e   # stop on any error

cd /app/
#exec OVERRIDE_WRITE_ACCESS_DB=1 python manage.py kv6sub &
exec uwsgi
