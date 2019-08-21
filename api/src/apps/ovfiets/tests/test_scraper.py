from unittest.mock import patch

from django.core.management import call_command
from django.test import TestCase

from apps.ovfiets.models import OvFietsRaw


@patch('apps.ovfiets.scraper.OvFietsScraper.fetch', autospec=True)
class TestOvFietsScraper(TestCase):
    def test_ok(self, fetch):
        fetch.side_effect = 'test'
        call_command('scrape_ovfiets')
        self.assertEqual(OvFietsRaw.objects.count(), 1)
