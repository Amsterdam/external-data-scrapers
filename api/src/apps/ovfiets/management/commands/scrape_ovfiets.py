import logging

from django.core.management.base import BaseCommand

from apps.ovfiets.scraper import OvFietsScraper

log = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Scrape OvFiets API"

    def handle(self, *args, **options):
        log.info("Starting Scraper")
        OvFietsScraper().start()
        log.info("Scraping Done")
