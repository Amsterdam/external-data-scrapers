from apps.base.managers import BaseSnapshotManager
from apps.ovfiets import models


class OvFietsSnapshotManager(BaseSnapshotManager):
    def get_import_model(self):
        return models.OvFiets
