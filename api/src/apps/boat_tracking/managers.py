from apps.base.managers import BaseSnapshotManager
from apps.boat_tracking import models


class BoatTrackingSnapshotManager(BaseSnapshotManager):
    def get_import_model(self):
        return models.BoatTracking
