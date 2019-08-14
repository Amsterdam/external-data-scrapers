from django.contrib.gis.db import models

from apps.base.managers import DistrictManager, NeighbourhoodManager


class Neighbourhood(models.Model):
    id = models.CharField(primary_key=True, max_length=255)
    code = models.CharField(max_length=255, blank=True, null=True)
    vollcode = models.CharField(max_length=255, blank=True, null=True)
    naam = models.CharField(max_length=255, blank=True, null=True)
    display = models.CharField(max_length=255, blank=True, null=True)
    type = models.CharField(max_length=255, blank=True, null=True)
    uri = models.CharField(max_length=255, blank=True, null=True)
    wkb_geometry = models.PolygonField(blank=True, null=True, srid=4326)

    # Using custom manager for get_neighbourhood method
    objects = NeighbourhoodManager()


class District(models.Model):
    id = models.CharField(primary_key=True, max_length=255)
    code = models.CharField(max_length=255, blank=True, null=True)
    naam = models.CharField(max_length=255, blank=True, null=True)
    display = models.CharField(max_length=255, blank=True, null=True)
    type = models.CharField(max_length=255, blank=True, null=True)
    uri = models.CharField(max_length=255, blank=True, null=True)
    wkb_geometry = models.PolygonField(blank=True, null=True, srid=4326)

    # Using custom manager for get_district method
    objects = DistrictManager()
