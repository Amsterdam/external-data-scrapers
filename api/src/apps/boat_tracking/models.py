from django.contrib.gis.db import models
from django.contrib.postgres.fields import JSONField

from apps.boat_tracking.managers import BoatTrackingRawManager


class BoatTrackingRaw(models.Model):
    scraped_at = models.DateTimeField(auto_now_add=True, editable=False)
    data = JSONField()

    objects = BoatTrackingRawManager()


class BoatTracking(models.Model):
    mmsi = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    type = models.IntegerField(null=True)
    length = models.IntegerField(null=True)
    width = models.IntegerField(null=True)
    geo_location = models.PointField(name='geo_location', srid=4326)
    speed = models.IntegerField()
    direction = models.IntegerField()
    status = models.IntegerField()
    sensor = models.CharField(max_length=255)
    lastupdate = models.DateTimeField()
    lastMoved = models.DateTimeField(null=True)

    scraped_at = models.DateTimeField()

    class Meta:
        ordering = ('scraped_at',)
