from unittest.mock import patch

from django.core.management import call_command
from django.test import TestCase

from apps.parkeergarages.models import (GuidanceSignSnapshot,
                                        ParkingLocationSnapshot)


@patch('apps.parkeergarages.scraper.ParkingLocationScraper.fetch', autospec=True)
class TestParkingLocationScraper(TestCase):
    def test_ok(self, fetch):
        fetch.side_effect = {'data': 'mock-json'}
        call_command('scrape_parkinglocation')
        self.assertEqual(ParkingLocationSnapshot.objects.count(), 1)


@patch('apps.parkeergarages.scraper.GuidanceSignScraper.fetch', autospec=True)
class TestGuidanceSignScraper(TestCase):
    def test_ok(self, fetch):
        fetch.side_effect = {'data': 'mock-json'}
        call_command('scrape_guidancesign')
        self.assertEqual(GuidanceSignSnapshot.objects.count(), 1)
