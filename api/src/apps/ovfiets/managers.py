from apps.base.managers import BaseRawManager
from apps.ovfiets import models


class OvFietsRawManager(BaseRawManager):
    def get_import_model(self):
        return models.OvFiets
