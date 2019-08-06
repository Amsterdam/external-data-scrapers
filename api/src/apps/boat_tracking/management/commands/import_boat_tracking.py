import logging

from django.core.management.base import BaseCommand

from apps.boat_tracking.importer import ImportBoatTracking

logging.basicConfig(level=logging.DEBUG, format='%(message)s')
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


class Command(BaseCommand):
    def handle(self, *args, **options):
        log.info("Starting import")
        ImportBoatTracking().start()
        log.info("import Done")
