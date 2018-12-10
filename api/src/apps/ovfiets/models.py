from django.conf import settings
from django.contrib.gis.db import models
from django.contrib.postgres.fields import JSONField


class OvFiets(models.Model):
    name = models.CharField(max_length=250)
    description = models.TextField()
    station_code = models.CharField(max_length=4, null=True)
    location_code = models.CharField(max_length=7)
    open = models.CharField(max_length=7)

    geometrie = models.PointField(name="geometrie", srid=4326, null=True)

    rental_bikes = models.IntegerField()
    fetch_time = models.DateTimeField()
    scraped_at = models.DateTimeField()
    stadsdeel = models.CharField(max_length=1)
    opening_hours = JSONField(null=True)
    unmapped = JSONField(null=True)

    class Meta:
        managed = settings.TESTING
        db_table = 'importer_ovfiets'
        ordering = ('location_code', 'id')
