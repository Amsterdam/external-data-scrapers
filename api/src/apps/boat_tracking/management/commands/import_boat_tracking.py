import logging

from django.core.management.base import BaseCommand

from apps.boat_tracking.importer import BoatTrackingImporter

log = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **options):
        log.info("Starting import")
        BoatTrackingImporter().start()
        log.info("import Done")
