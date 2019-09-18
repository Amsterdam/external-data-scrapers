import logging

from apps.base.areas_importer import AreasImportFactory
from apps.base.base_importer import BaseSnapshotImporter
from apps.base.geojson_importer import GeoJsonImportFactory
from apps.parkeergarages import constants
from apps.parkeergarages.forms import ParkingLocationImporterForm
from apps.parkeergarages.models import ParkingLocation

log = logging.getLogger(__name__)


class ParkingLocationImportFactory(GeoJsonImportFactory, AreasImportFactory):
    raw_to_model_fields = constants.PARKINGLOCATION_RAW_TO_MODEL_FIELDS
    model_form = ParkingLocationImporterForm


class ParkingLocationImporter(BaseSnapshotImporter):
    import_factory = ParkingLocationImportFactory
    import_model = ParkingLocation

    def fetch_raw_data_from_snapshot(self):
        return self.snapshot.data['features']
