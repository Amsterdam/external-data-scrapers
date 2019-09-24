import logging

from django.core.management.base import BaseCommand

from apps.ovfiets.importer import OvFietsSnapshotImporter
from apps.ovfiets.models import OvFietsSnapshot

log = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **options):
        log.info("Starting Import")
        for snapshot in OvFietsSnapshot.objects.limit_offset_iterator(10):
            OvFietsSnapshotImporter(snapshot).start_import()
        log.info("Importing Done")
