from django.contrib.gis.db import models
from django.contrib.postgres.fields import JSONField


class BoatTrackingRaw(models.Model):
    scraped_at = models.DateTimeField(auto_now_add=True, editable=False)
    data = JSONField()
