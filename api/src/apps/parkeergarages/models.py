from django.contrib.gis.db import models
from django.contrib.postgres.fields import JSONField

from apps.constants import WGS84_SRID
from apps.parkeergarages.managers import (GuidanceSignSnapshotManager,
                                          ParkingLocationSnapshotManager)


class ParkingLocationSnapshot(models.Model):
    id = models.BigAutoField(primary_key=True, unique=True)
    scraped_at = models.DateTimeField(auto_now_add=True, editable=False, db_index=True)
    data = JSONField()

    objects = ParkingLocationSnapshotManager()

    class Meta:
        db_table = 'parkinglocation_raw'
        ordering = ('scraped_at', 'id')


class GuidanceSignSnapshot(models.Model):
    id = models.BigAutoField(primary_key=True, unique=True)
    scraped_at = models.DateTimeField(auto_now_add=True, editable=False, db_index=True)
    data = JSONField()

    objects = GuidanceSignSnapshotManager()

    class Meta:
        db_table = 'guidancesign_raw'
        ordering = ('scraped_at', 'id')


class ParkingLocation(models.Model):
    api_id = models.CharField(max_length=255)
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=20)
    geometrie = models.PointField(name="geometrie", srid=WGS84_SRID, null=True)
    state = models.CharField(max_length=10)

    free_space_short = models.IntegerField(
        blank=True, null=True, default=None, help_text='Short duration parking availability'
    )
    free_space_long = models.IntegerField(
        blank=True, null=True, default=None, help_text='Long duration parking availability'
    )
    short_capacity = models.IntegerField(
        blank=True, null=True, default=None, help_text='Short duration parking capacity'
    )
    long_capacity = models.IntegerField(
        blank=True, null=True, default=None, help_text='Long duration parking capacity'
    )

    pub_date = models.DateTimeField()
    stadsdeel = models.CharField(max_length=1, null=True)
    buurt_code = models.CharField(max_length=10, null=True)
    scraped_at = models.DateTimeField(null=True)

    class Meta:
        db_table = 'importer_parkinglocation'
        ordering = ('-pub_date',)


class GuidanceSign(models.Model):
    api_id = models.CharField(max_length=255, unique=True)
    geometrie = models.PointField(name="geometrie", srid=WGS84_SRID, null=True)
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=20)
    state = models.CharField(max_length=10)
    pub_date = models.DateTimeField()
    removed = models.NullBooleanField()
    stadsdeel = models.CharField(max_length=1, null=True)
    buurt_code = models.CharField(max_length=10, null=True)
    scraped_at = models.DateTimeField()

    def __str__(self):
        return '{} - {}'.format(self.name, self.api_id)

    class Meta:
        db_table = 'importer_guidancesign'
        ordering = ('-pub_date',)


class ParkingGuidanceDisplay(models.Model):
    api_id = models.CharField(max_length=255)
    pub_date = models.DateTimeField()
    description = models.TextField()
    type = models.CharField(max_length=50)
    output = models.CharField(max_length=100, blank=True)
    output_description = models.CharField(max_length=255, blank=True)
    scraped_at = models.DateTimeField()
    guidance_sign = models.ForeignKey(
        'GuidanceSign',
        to_field='api_id',
        on_delete=models.CASCADE,
        related_name='displays'
    )

    class Meta:
        db_table = 'importer_parkingguidancedisplay'
        ordering = ('-pub_date',)
