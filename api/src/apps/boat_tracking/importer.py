import logging

from apps.base.base_importer import BaseImportFactory, BaseSnapshotImporter
from apps.boat_tracking import constants
from apps.boat_tracking.forms import BoatTrackingImporterForm
from apps.boat_tracking.models import BoatTracking

log = logging.getLogger(__name__)


class BoatTrackingImportFactory(BaseImportFactory):
    raw_to_model_fields = constants.BOAT_TRACKING_RAW_TO_MODEL_MAPPING
    model_form = BoatTrackingImporterForm
    areas_fields = {
        'neighbourhood_field': 'buurt_code',
        'district_field': 'stadsdeel',
        'geometry_field': 'geo_location'
    }


class BoatTrackingSnapshotImporter(BaseSnapshotImporter):
    import_factory = BoatTrackingImportFactory
    import_model = BoatTracking
