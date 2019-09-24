import logging

from django.core.management.base import BaseCommand

from apps.boat_tracking.importer import BoatTrackingSnapshotImporter
from apps.boat_tracking.models import BoatTrackingSnapshot

log = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **options):
        log.info("Starting import")
        for snapshot in BoatTrackingSnapshot.objects.limit_offset_iterator(10):
            BoatTrackingSnapshotImporter(snapshot).start_import()
        log.info("import Done")
