import logging

from apps.base.areas_importer import AreasImportFactory
from apps.base.base_importer import BaseSnapshotImporter
from apps.ovfiets import constants
from apps.ovfiets.forms import OvFietsImporterForm
from apps.ovfiets.models import OvFiets

log = logging.getLogger(__name__)


class OvFietsImportFactory(AreasImportFactory):
    raw_to_model_fields = constants.OVFIETS_RAW_TO_MODEL_MAPPING
    model_form = OvFietsImporterForm

    def prepare_extra(self, raw_data):
        '''
        Extract the nested `extra` json to the root of the raw_data
        '''
        extra = raw_data.pop('extra')
        raw_data.update(extra)
        return raw_data

    def prepare_coordinates(self, raw_data):
        '''
        Combine `lng` and `lat` json keys into one geometrie key
        '''
        raw_data['geometrie'] = [raw_data.pop('lng'), raw_data.pop('lat')]
        return raw_data

    def prepare_unmapped(self, raw_data):
        unmapped = {}

        for key in raw_data.keys():
            if key not in constants.OVFIETS_FORM_FIELDS:
                unmapped[key] = raw_data[key]

        raw_data['unmapped'] = unmapped
        return raw_data

    def prepare_raw_data(self, raw_data):
        raw_data = self.prepare_extra(raw_data)
        raw_data = self.prepare_coordinates(raw_data)

        # Super is called midway because prepare_unmapped expects needs the raw keys to be converted
        raw_data = super().prepare_raw_data(raw_data)

        return self.prepare_unmapped(raw_data)


class OvFietsSnapshotImporter(BaseSnapshotImporter):
    import_factory = OvFietsImportFactory
    import_model = OvFiets

    def fetch_raw_data_from_snapshot(self):
        return self.snapshot.data['locaties'].values()
