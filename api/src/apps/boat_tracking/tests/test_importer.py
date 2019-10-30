from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone

from apps.boat_tracking.models import BoatTracking, BoatTrackingSnapshot


class TestBoatTrackingImporter(TestCase):
    fixtures = ['boat_tracking_test.json']

    def test_ok(self):
        call_command('import_boat_tracking')
        self.assertEqual(BoatTracking.objects.count(), 18)

    def test_extra_field_ignored(self):
        BoatTrackingSnapshot.objects.all().delete()
        BoatTrackingSnapshot.objects.create(data=[{
            'Id': '120',
            'ExtraField': 12,
            "Sensor": 'test',
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
        iterator = BoatTrackingSnapshot.objects.query_iterator(2)

        self.assertEqual(len(next(iterator)), 2)
        self.assertEqual(len(next(iterator)), 2)
        self.assertEqual(len(next(iterator)), 1)

        with self.assertRaises(StopIteration):
            next(iterator)

    def test_only_latest(self):
        call_command('import_boat_tracking')
        self.assertEqual(BoatTracking.objects.count(), 18)

        hour_later = timezone.now() + timezone.timedelta(hours=1)
        BoatTrackingSnapshot.objects.filter(pk=1).update(scraped_at=hour_later)

        call_command('import_boat_tracking')
        self.assertEqual(BoatTracking.objects.count(), 21)

    def test_correct_timezone(self):
        call_command('import_boat_tracking')

        boat_tracking = BoatTracking.objects.order_by('id').first()
        correct_pub_date = timezone.datetime(2019, 7, 24, 14, 18)

        self.assertEqual(boat_tracking.lastupdate.date(), correct_pub_date.date())
        self.assertEqual(boat_tracking.lastupdate.hour, correct_pub_date.hour)
        self.assertEqual(boat_tracking.lastupdate.minute, correct_pub_date.minute)

        correct_scraped_at = timezone.datetime(2019, 7, 24, 14, 26)

        self.assertEqual(boat_tracking.scraped_at.date(), correct_scraped_at.date())
        self.assertEqual(boat_tracking.scraped_at.hour, correct_scraped_at.hour)
        self.assertEqual(boat_tracking.scraped_at.minute, correct_scraped_at.minute)
