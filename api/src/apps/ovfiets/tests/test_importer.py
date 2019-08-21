from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone

from apps.ovfiets.models import OvFiets, OvFietsRaw


class TestOvFietsImporter(TestCase):
    fixtures = ['ovfiets_raw.json']

    def test_ok(self):
        call_command('import_ovfiets')
        self.assertEqual(OvFiets.objects.count(), 4)

        ovfiets = OvFiets.objects.filter(id=1)[0]
        self.assertEqual(ovfiets.location_code, "o001")
        self.assertEqual(ovfiets.rental_bikes, 3)
        self.assertEqual(ovfiets.geometrie.srid, 4326)

    def test_iterate_raw_model(self):
        iterator = OvFietsRaw.objects.query_iterator(1)

        self.assertEqual(len(next(iterator)), 1)
        self.assertEqual(len(next(iterator)), 1)

        with self.assertRaises(StopIteration):
            self.assertIsNone(next(iterator))

    def test_only_latest(self):
        call_command('import_ovfiets')
        self.assertEqual(OvFiets.objects.count(), 4)

        hour_later = timezone.now() + timezone.timedelta(hours=1)
        OvFietsRaw.objects.filter(pk=1).update(scraped_at=hour_later)

        call_command('import_ovfiets')
        self.assertEqual(OvFiets.objects.count(), 6)
