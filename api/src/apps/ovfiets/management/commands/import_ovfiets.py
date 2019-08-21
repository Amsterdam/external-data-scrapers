import logging

from django.core.management.base import BaseCommand

from apps.ovfiets.importer import OvFietsImporter

log = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Import OvFiets from OvFietsRaw"

    def handle(self, *args, **options):
        log.info("Starting Import")
        OvFietsImporter().start()
        log.info("Importing Done")
