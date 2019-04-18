# Realtime kv6posinfo scraper (kv6sub.py)

The Kv6Posinfo feed is an ZeroMQ feed provided by tcp://pubsub.besteffort.ndovloket.nl:7658.
The client (ip address) should be whitelisted by ovloket in order to receive the data. 

## Static data

The client requires the static data from http://gtfs.ovapi.nl/nl/gtfs-nl.zip
This file contains trips and routes for the comming weeks. The archive should be reloaded every week.
[refresh_stop_data.sh](api/deploy/ovlookup_data/refresh_stop_data.sh)

file  | contents
----- | --------
stops.txt | stops and their userstopcode (used in kv6posinfo)
trips.txt | planned trips for the comming weeks. Use shape id to link to shapes (and geo locations)
shapes.txt | shape of a trip. It also contains stops sequences and cumulative travelled distance
stop_times.txt | planned stops for the public transport

The following data is created from the static data:

table | contents
----- | --------
ov_ovstop | lookup table of stopcode with geo location (SRID=4326)
ov_ovroutes | all trips that have stops in a bounding box around Amsterdam
ov_OvRouteSection | for ov_ovroutes entry sequence, store stopcode and distance travelled

These tables will be used by the kv6sub client.

## Postgresql partitions

The realtime ov data is stored in Postgresql partitions. The partitions range has been set to a week. 
A job should be run weekly to create new partitions [dc-import-trips.sh](api/deploy/ovlookup_data/dc-import-trips.sh). 

```
# or manually from the cmd line
python manage.py kv6partition
```

# kv6sub.py

The kv6sub client should run as a service. The client inherits [ZmqBaseClient](api/src/apps/ov/zmq_base_client.py). 
The ZmqBaseClient class handles reconnect and retry. A client can have multiple ZmqSubscribers. 
(Add new subscribers in self.subscribers[])

Currently only the kv6subscriber has been implemented. A subscriber must inherit [ZmqSubscriber](api/src/apps/ov/zmq_subscriber.py).
Within this class 2 methods should be implemented:

* handle_refreshdata (init lookup data, is invoked once a day)
* handle_message (handle actual message, callback)

Kv6XMLProcessor.process is invoked for every message received. Within that process the following actions
will be performed:
* check if a message is 'valid'
* archive raw message
* only process messages of routes that are in the ov_ovroutes table (this table is cached in memory)
* for every message in the bounding box (== route is in ovroutes table)
    * Add geo location based on the userstopcode (uses cached table ov_ovstop)
    * Compute travel time and lookup travel distance between stops. Waiting time at the first stop 
      should not to be included in the travel time.
        * Travel time from first stop to second stop: current_stop.arrival - prev_stop.departure
        * Travel time from second stop: current_stop.arrival - prev_stop.arrival

To add a subscriber for the NS feed, create a new subscriber and inherit ZmqSubscriber.
Override handle_refreshdata and handle_message and this subscriber in self.subscribers[].


# Archiving data

The Raw realtime data is archived by [archive-tables.sh](api/deploy/archive/archive-tables.sh)
The following actions will be performed:
* dump postgres sql copy format - data (gzip)
* dump schema
* tar the resulting archives
* upload tar file to objectstore
* cleanup tmp files
* truncate tables IF ONLY everything was successfull. (and if --empty-table argument is supplied)

The following env vars are required:
```
# postgresql settings
PGUSER
PGDATABASE
PGHOST
PGPASSWORD

# object store settings
TENANT_NAME
TENANT_ID
OBJECTSTORE_USER
OBJECTSTORE_PASSWORD
```

# Summarize data

The real time parsed data is summarized every week by [sum.sql](api/deploy/ovlookup_data/sum.sql)
The sql script is made idempotent. The data is compacted and stored per journey and travelled distance.
Currently 3 buckets have been defined.

* 06-09 Morning rush hour
* 18-18 Evening rush hour
* other

Multiple sets with different slices are supported. For every compacted row the distance and time will be stored.