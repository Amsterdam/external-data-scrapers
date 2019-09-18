import logging

from django.core.management.base import BaseCommand

from apps.parkeergarages.importer import ParkingLocationImporter
from apps.parkeergarages.models import ParkingLocationSnapshot

log = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Import ParkingLocationSnapshot"

    def handle(self, *args, **options):
        log.info("Starting Importing")
        for snapshot in ParkingLocationSnapshot.objects.limit_offset_iterator(10):
            ParkingLocationImporter(snapshot).start_import()
        log.info("Import Done")
