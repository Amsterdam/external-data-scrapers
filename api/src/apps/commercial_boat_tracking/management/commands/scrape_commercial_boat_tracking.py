import logging

from django.core.management.base import BaseCommand

from apps.commercial_boat_tracking.scraper import ComBoatTrackingScraper

logging.basicConfig(level=logging.DEBUG, format='%(message)s')
log = logging.getLogger(__name__)
log.setLevel(logging.ERROR)


class Command(BaseCommand):
    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        log.info("Starting Scraper")
        ComBoatTrackingScraper().start()
        log.info("Scraping Done")
