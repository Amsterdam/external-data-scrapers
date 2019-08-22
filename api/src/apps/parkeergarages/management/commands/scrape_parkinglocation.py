import logging

from django.core.management.base import BaseCommand

from apps.parkeergarages.scraper import ParkingLocationScraper

log = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Scrape parkeergarages"

    def handle(self, *args, **options):
        log.info("Starting Scraper")
        ParkingLocationScraper().start()
        log.info("Scraping Done")
