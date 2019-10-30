from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone

from apps.parkeergarages.models import (GuidanceSign, GuidanceSignSnapshot,
                                        ParkingGuidanceDisplay,
                                        ParkingLocation,
                                        ParkingLocationSnapshot)


class TestParkingLocationImporter(TestCase):
    fixtures = ['parkeergarages.json']

    def test_ok(self):
        call_command('import_parkinglocation')
        self.assertEqual(ParkingLocation.objects.count(), 3)

        parkinglocation = ParkingLocation.objects.order_by('id').first()
        self.assertEqual(parkinglocation.name, 'CE-P28 PTA Touringcars')
        self.assertEqual(parkinglocation.long_capacity, None)
        self.assertEqual(parkinglocation.short_capacity, 42)
        self.assertEqual(parkinglocation.free_space_short, 0)
        self.assertEqual(parkinglocation.free_space_long, None)
        self.assertEqual(parkinglocation.geometrie.srid, 4326)

    def test_iterate_raw_model(self):
        iterator = ParkingLocationSnapshot.objects.limit_offset_iterator(1)

        self.assertEqual(next(iterator), ParkingLocationSnapshot.objects.get(id=1))
        self.assertEqual(next(iterator), ParkingLocationSnapshot.objects.get(id=2))

        with self.assertRaises(StopIteration):
            next(iterator)

    def test_only_latest(self):
        call_command('import_parkinglocation')
        self.assertEqual(ParkingLocation.objects.count(), 3)

        hour_later = timezone.now() + timezone.timedelta(hours=1)
        ParkingLocationSnapshot.objects.filter(pk=1).update(scraped_at=hour_later)

        call_command('import_parkinglocation')
        self.assertEqual(ParkingLocation.objects.count(), 5)

    def test_correct_timezone(self):
        call_command('import_parkinglocation')
        self.assertEqual(ParkingLocation.objects.count(), 3)

        parkinglocation = ParkingLocation.objects.order_by('id').first()
        correct_pub_date = timezone.datetime(2019, 8, 28, 13, 49)

        self.assertEqual(parkinglocation.pub_date.date(), correct_pub_date.date())
        self.assertEqual(parkinglocation.pub_date.hour, correct_pub_date.hour)
        self.assertEqual(parkinglocation.pub_date.minute, correct_pub_date.minute)

        correct_scraped_at = timezone.datetime(2019, 8, 28, 13, 50)

        self.assertEqual(parkinglocation.scraped_at.date(), correct_scraped_at.date())
        self.assertEqual(parkinglocation.scraped_at.hour, correct_scraped_at.hour)
        self.assertEqual(parkinglocation.scraped_at.minute, correct_scraped_at.minute)


class TestGuidanceSignImporter(TestCase):
    fixtures = ['parkeergarages.json']

    def test_ok(self):
        call_command('import_guidancesign')
        self.assertEqual(GuidanceSign.objects.count(), 3)
        self.assertEqual(ParkingGuidanceDisplay.objects.count(), 7)

        guidancesign = GuidanceSign.objects.order_by('id').first()
        self.assertEqual(guidancesign.name, 'FJ462B13 - ZO-B13 Burg.Stramanweg 02510/080')
        self.assertEqual(guidancesign.state, 'ok')
        self.assertEqual(guidancesign.type, 'guidancesign')
        self.assertEqual(guidancesign.geometrie.srid, 4326)

        parkingguidancedisplay = ParkingGuidanceDisplay.objects.order_by('id').first()
        self.assertEqual(parkingguidancedisplay.output, 'X')

    def test_iterate_raw_model(self):
        iterator = GuidanceSignSnapshot.objects.limit_offset_iterator(1)

        self.assertEqual(next(iterator), GuidanceSignSnapshot.objects.get(id=1))
        self.assertEqual(next(iterator), GuidanceSignSnapshot.objects.get(id=2))

        with self.assertRaises(StopIteration):
            next(iterator)

    def test_guidance_sign_ignored(self):
        call_command('import_guidancesign')
        self.assertEqual(GuidanceSign.objects.count(), 3)

        hour_later = timezone.now() + timezone.timedelta(hours=1)
        GuidanceSignSnapshot.objects.filter(id=1).update(scraped_at=hour_later)

        call_command('import_guidancesign')
        self.assertEqual(GuidanceSign.objects.count(), 3)

    def test_only_latest(self):
        call_command('import_guidancesign')
        self.assertEqual(ParkingGuidanceDisplay.objects.count(), 7)

        hour_later = timezone.now() + timezone.timedelta(hours=1)
        GuidanceSignSnapshot.objects.filter(pk=1).update(scraped_at=hour_later)

        call_command('import_guidancesign')
        self.assertEqual(ParkingGuidanceDisplay.objects.count(), 11)

    def test_correct_timezone(self):
        call_command('import_guidancesign')
        self.assertEqual(GuidanceSign.objects.count(), 3)
        self.assertEqual(ParkingGuidanceDisplay.objects.count(), 7)

        guidancesign = GuidanceSign.objects.order_by('id').first()
        correct_pub_date = timezone.datetime(2019, 8, 28, 13, 49)

        self.assertEqual(guidancesign.pub_date.date(), correct_pub_date.date())
        self.assertEqual(guidancesign.pub_date.hour, correct_pub_date.hour)
        self.assertEqual(guidancesign.pub_date.minute, correct_pub_date.minute)

        correct_scraped_at = timezone.datetime(2019, 8, 28, 13, 50)

        self.assertEqual(guidancesign.scraped_at.date(), correct_scraped_at.date())
        self.assertEqual(guidancesign.scraped_at.hour, correct_scraped_at.hour)
        self.assertEqual(guidancesign.scraped_at.minute, correct_scraped_at.minute)
