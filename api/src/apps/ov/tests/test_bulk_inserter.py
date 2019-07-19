from django.test import TestCase

from apps.ov import models
from apps.ov.bulk_inserter import BulkInserter


class TestBulkInserter(TestCase):

    def test_error(self):
        bulk_inserter = BulkInserter(models.OvRaw, batch_size=2)

        bulk_inserter.add(models.OvRaw(id='H'))  # Use string for id to invoke error
        self.assertEqual(len(bulk_inserter.batch), 1)

        # Error should occur when adding second instance
        with self.assertRaises(ValueError):
            bulk_inserter.add(models.OvRaw(id=1))

        # Batch should be cleared
        self.assertEqual(len(bulk_inserter.batch), 0)
