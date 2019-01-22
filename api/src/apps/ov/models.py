# from django.conf import settings
# from django.contrib.postgres.fields import JSONField
from django.contrib.gis.db import models


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
    operatingday = models.DateField()
    dataownercode = models.CharField(max_length=255)
    lineplanningnumber = models.CharField(max_length=255)
    journeynumber = models.IntegerField(),
    reinforcementnumber = models.SmallIntegerField()
    userstopcode = models.CharField(max_length=255)
    passagesequencenumber = models.SmallIntegerField()
    distancesincelastuserstop = models.IntegerField()
    punctuality = models.IntegerField()
    rd_x = models.IntegerField()
    rd_y = models.IntegerField()
    blockcode = models.IntegerField()
    vehiclenumber = models.IntegerField()
    wheelchairaccessible = models.CharField(max_length=255)
    source = models.CharField(max_length=255)
    numberofcoaches = models.SmallIntegerField(),
    trip_hash = models.BigIntegerField()
