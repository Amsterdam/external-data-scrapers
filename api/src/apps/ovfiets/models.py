from django.contrib.gis.db import models
from django.contrib.postgres.fields import JSONField

from apps.ovfiets.managers import OvFietsRawManager


class OvFietsRaw(models.Model):
    id = models.BigAutoField(primary_key=True, unique=True)
    scraped_at = models.DateTimeField(auto_now_add=True, editable=False, db_index=True)
    data = JSONField()

    objects = OvFietsRawManager()

    class Meta:
        db_table = 'ovfiets_raw'
        ordering = ('scraped_at', 'id')


class OvFiets(models.Model):
    id = models.BigAutoField(primary_key=True, unique=True)
    name = models.CharField(max_length=250)
    description = models.TextField(null=True)
    station_code = models.CharField(max_length=4, null=True)
    location_code = models.CharField(max_length=7)
    open = models.CharField(max_length=7)

    geometrie = models.PointField(name="geometrie", srid=4326, null=True)

    rental_bikes = models.IntegerField(null=True)
    fetch_time = models.DateTimeField(db_index=True)
    scraped_at = models.DateTimeField(db_index=True)
    stadsdeel = models.CharField(max_length=4, null=True)
    buurt_code = models.CharField(max_length=5, null=True)
    opening_hours = JSONField(null=True)
    unmapped = JSONField(null=True)

    class Meta:
        db_table = 'importer_ovfiets'
        ordering = ('location_code', 'id')
