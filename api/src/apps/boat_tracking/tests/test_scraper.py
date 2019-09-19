from unittest.mock import patch

from django.core.management import call_command
from django.test import TestCase, override_settings

from apps.boat_tracking.models import BoatTrackingSnapshot
from apps.boat_tracking.scraper import InvalidCredentials, MissingEnvVariables


@override_settings(WATERNET_PASSWORD='test', WATERNET_USERNAME='test')
@patch('apps.boat_tracking.scraper.BoatTrackingScraper.requests', autospec=True)
class TestBoatTrackingScraper(TestCase):

    @override_settings(WATERNET_PASSWORD=None, WATERNET_USERNAME=None)
    def test_missing_credentials(self, requests):
        with self.assertRaises(MissingEnvVariables):
            call_command('scrape_boat_tracking')
        self.assertEqual(BoatTrackingSnapshot.objects.count(), 0)

    def test_403_response(self, requests):
        requests.post().status_code = 403
        with self.assertRaises(InvalidCredentials):
            call_command('scrape_boat_tracking')
        self.assertEqual(BoatTrackingSnapshot.objects.count(), 0)

    def test_ok(self, requests):
        requests.post().status_code = 200
        requests.get().json.side_effect = 'test'
        call_command('scrape_boat_tracking')
        self.assertEqual(BoatTrackingSnapshot.objects.count(), 1)
