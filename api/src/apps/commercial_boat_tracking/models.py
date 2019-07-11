from django.contrib.postgres.fields import JSONField
from django.db import models


class CommercialBoatTrackingRaw(models.Model):
    scraped_at = models.DateTimeField(auto_now_add=True, editable=False)
    data = JSONField()
