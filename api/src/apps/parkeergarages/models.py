from django.conf import settings
from django.contrib.gis.db import models


class ParkingLocation(models.Model):
    api_id = models.CharField(max_length=255)
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=20)
    geometrie = models.PointField(name="geometrie", srid=4326, null=True)
    state = models.CharField(max_length=10)
    free_space_short = models.IntegerField()
    free_space_long = models.IntegerField()
    short_capacity = models.IntegerField()
    long_capacity = models.IntegerField()
    pub_date = models.DateTimeField()
    stadsdeel = models.CharField(max_length=1)
    buurt_code = models.CharField(max_length=10)
    scraped_at = models.DateTimeField()

    class Meta:
        managed = settings.TESTING
        db_table = 'importer_parkinglocation'
        ordering = ('-pub_date',)


class GuidanceSign(models.Model):
    api_id = models.CharField(max_length=255, unique=True)
    geometrie = models.PointField(name="geometrie", srid=4326, null=True)
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=20)
    state = models.CharField(max_length=10)
    pub_date = models.DateTimeField()
    removed = models.NullBooleanField()
    stadsdeel = models.CharField(max_length=1)
    buurt_code = models.CharField(max_length=10)
    scraped_at = models.DateTimeField()

    def __str__(self):
        return '{} - {}'.format(self.name, self.api_id)

    class Meta:
        managed = settings.TESTING
        db_table = 'importer_guidancesign'
        ordering = ('-pub_date',)


class ParkingGuidanceDisplay(models.Model):
    api_id = models.CharField(max_length=255)
    pub_date = models.DateTimeField()
    description = models.TextField()
    type = models.CharField(max_length=50)
    output = models.CharField(max_length=100)
    output_description = models.CharField(max_length=255)
    scraped_at = models.DateTimeField()
    guidance_sign = models.ForeignKey(
        'GuidanceSign',
        to_field='api_id',
        on_delete=models.DO_NOTHING,
        related_name='displays'
    )

    class Meta:
        managed = settings.TESTING
        db_table = 'importer_parkingguidancedisplay'
        ordering = ('-pub_date',)
