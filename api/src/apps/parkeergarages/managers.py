from apps.base.managers import BaseRawManager
from apps.parkeergarages import models


class ParkingLocationManager(BaseRawManager):
    def get_import_model(self):
        return models.ParkingLocation


class GuidanceSignManager(BaseRawManager):
    def get_import_model(self):
        return models.GuidanceSign
