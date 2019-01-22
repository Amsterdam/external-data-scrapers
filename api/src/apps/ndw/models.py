from django.conf import settings
from django.contrib.gis.db import models


class TravelTime(models.Model):
    measurement_site_reference = models.CharField(max_length=255)
    computational_method = models.CharField(
        max_length=255, blank=True, null=True
    )
    number_of_incomplete_input = models.IntegerField()
    number_of_input_values_used = models.IntegerField()
    standard_deviation = models.FloatField()
    supplier_calculated_data_quality = models.FloatField()
    duration = models.FloatField()
    data_error = models.NullBooleanField()
    measurement_time = models.DateTimeField()
    scraped_at = models.DateTimeField()

    class Meta:
        db_table = 'importer_traveltime'
        managed = settings.TESTING
        ordering = ('-scraped_at',)


class ThirdpartyTravelTime(models.Model):
    measurement_site_reference = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=2)
    length = models.IntegerField()
    geometrie = models.LineStringField(name="geometrie", srid=4326, null=True)
    timestamp = models.DateTimeField()
    scraped_at = models.DateTimeField()

    class Meta:
        db_table = "importer_thirdparty_traveltime"
        managed = settings.TESTING
        ordering = ('-scraped_at', )
