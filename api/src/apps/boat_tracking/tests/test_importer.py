from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone

from apps.boat_tracking.models import BoatTracking, BoatTrackingRaw


class TestBoatTrackingImporter(TestCase):
    fixtures = ['boat_tracking_test.json']

    def test_ok(self):
        call_command('import_boat_tracking')
        self.assertEqual(BoatTracking.objects.count(), 18)

    def test_extra_field_ignored(self):
        BoatTrackingRaw.objects.all().delete()
        BoatTrackingRaw.objects.create(data=[{
            'Id': '120',
            'ExtraField': 12,
            "Speed": 1,
            'Position': {
                "x": 4.919753551483154,
                "y": 52.3687858581543
            },
            'Direction': 2658,
            'Status': 15,
            'Lastupdate': "2019-07-24T14:18:06.000Z"
        }])
        call_command('import_boat_tracking')
        self.assertEqual(BoatTracking.objects.count(), 1)

    def test_iterate_raw_model(self):
        iterator = BoatTrackingRaw.objects.query_iterator(2)

        self.assertEqual(len(next(iterator)), 2)
        self.assertEqual(len(next(iterator)), 2)
        self.assertEqual(len(next(iterator)), 1)

        with self.assertRaises(StopIteration):
            next(iterator)

    def test_only_latest(self):
        call_command('import_boat_tracking')
        self.assertEqual(BoatTracking.objects.count(), 18)

        hour_later = timezone.now() + timezone.timedelta(hours=1)
        BoatTrackingRaw.objects.filter(pk=1).update(scraped_at=hour_later)

        call_command('import_boat_tracking')
        self.assertEqual(BoatTracking.objects.count(), 21)
