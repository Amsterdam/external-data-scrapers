import logging

from django.core.management.base import BaseCommand

from apps.boat_tracking.scraper import BoatTrackingScraper

logging.basicConfig(level=logging.DEBUG, format='%(message)s')
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


class Command(BaseCommand):
    def handle(self, *args, **options):
        log.info("Starting Scraper")
        BoatTrackingScraper().start()
        log.info("Scraping Done")
