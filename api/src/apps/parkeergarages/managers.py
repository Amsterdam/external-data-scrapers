from apps.base.managers import BaseSnapshotManager
from apps.parkeergarages import models


class ParkingLocationSnapshotManager(BaseSnapshotManager):
    def get_import_model(self):
        return models.ParkingLocation


class GuidanceSignSnapshotManager(BaseSnapshotManager):
    def get_import_model(self):
        return models.GuidanceSign
