from apps.base.managers import BaseRawManager
from apps.boat_tracking import models


class BoatTrackingRawManager(BaseRawManager):
    def get_import_model(self):
        return models.BoatTracking
