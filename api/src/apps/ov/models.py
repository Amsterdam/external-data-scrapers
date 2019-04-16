from django.contrib.gis.db import models
from django.contrib.gis.db.models import PointField


# Create your models here.
class OvRaw(models.Model):
    id = models.BigAutoField(primary_key=True)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    feed = models.CharField(max_length=255)
    xml = models.BinaryField()


"""
kv6 table defined by ov loket
CREATE MERGE TABLE "sys"."kv6" (
"receive" TIMESTAMP,
"message" TIMESTAMP,
"vehicle" TIMESTAMP,
"messagetype" VARCHAR(10),
"operatingday" DATE,
"dataownercode" VARCHAR(10),
"lineplanningnumber" VARCHAR(10),
"journeynumber" INTEGER,
"reinforcementnumber" SMALLINT,
"userstopcode" VARCHAR(10),
"passagesequencenumber" SMALLINT,
"distancesincelastuserstop" INTEGER,
"punctuality" INTEGER,
"rd_x" INTEGER,
"rd_y" INTEGER,
"blockcode" INTEGER,
"vehiclenumber" INTEGER,
"wheelchairaccessible" VARCHAR(5),
"source" VARCHAR(10),
"numberofcoaches" SMALLINT,
"trip_hash" BIGINT
);
"""


class OvKv6(models.Model):
    id = models.BigAutoField(primary_key=True)
    receive = models.DateTimeField()
    message = models.DateTimeField()
    vehicle = models.DateTimeField()
    messagetype = models.CharField(max_length=255)
    operatingday = models.DateField(db_index=True)
    dataownercode = models.CharField(max_length=255)
    lineplanningnumber = models.CharField(max_length=255)
    journeynumber = models.IntegerField()
    reinforcementnumber = models.SmallIntegerField(null=True)
    userstopcode = models.CharField(null=True, max_length=255)
    passagesequencenumber = models.SmallIntegerField(null=True)
    distancesincelastuserstop = models.IntegerField(null=True)
    punctuality = models.IntegerField(null=True)
    rd_x = models.IntegerField(null=True)
    rd_y = models.IntegerField(null=True)
    blockcode = models.IntegerField(null=True)
    vehiclenumber = models.IntegerField(null=True)
    wheelchairaccessible = models.CharField(null=True, max_length=255)
    source = models.CharField(max_length=255)
    numberofcoaches = models.SmallIntegerField(null=True)
    trip_hash = models.BigIntegerField(null=True)
    geo_location = PointField(srid=28992, null=True)
    distance = models.IntegerField(null=True)
    time = models.IntegerField(null=True)
    prev_geo_location = PointField(srid=28992, null=True)
    prev_userstopcode = models.CharField(null=True, max_length=255)


class OvStop(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    stop_id = models.CharField(max_length=255, null=True, db_index=True)
    name = models.CharField(max_length=255)
    geo_location = PointField(srid=4326)


# key format: 'dataownercode:lineplanningnumber:journeynumber'
class OvRoutes(models.Model):
    key = models.CharField(max_length=255, primary_key=True)
    route_id = models.IntegerField()
    service_id = models.IntegerField()
    trip_id = models.IntegerField()
    headsign = models.CharField(max_length=255, null=True)
    short_name = models.CharField(max_length=255, null=True)
    long_name = models.CharField(max_length=255, null=True)


class OvRouteSection(models.Model):
    stop_id = models.CharField(max_length=255, db_index=True)
    stop_code = models.CharField(max_length=255, db_index=True)
    stop_sequence = models.IntegerField()
    shape_dist_traveled = models.IntegerField()
    route = models.ForeignKey(OvRoutes, on_delete=models.CASCADE)
