from datetime import datetime, timedelta

from django.test import TestCase

from apps.ov.partition_util import PartitionUtil


class TestPartition(TestCase):
    def setUp(self):
        self.part = PartitionUtil()
        self.day = datetime(2019, 2, 5)

    def test_partitions(self):
        dp = self.part.day_partition(self.day)
        self.assertEqual(dp[0].date(), self.day.date())
        self.assertEqual(dp[1].date(), (self.day + timedelta(1)).date())

        dw = self.part.week_partition(self.day)
        self.assertEqual(dw[0].date(), datetime(2019, 2, 4).date())
        self.assertEqual(dw[1].date(), datetime(2019, 2, 11).date())

        dm = self.part.month_partition(self.day)
        self.assertEqual(dm[0].date(), datetime(2019, 2, 1).date())
        self.assertEqual(dm[1].date(), datetime(2019, 3, 1).date())

        q = self.part.make_partition_query('t', dm)
        expected = "create table if not exists t_20190201 partition of t"\
                   " for values from ('20190201') to ('20190301');"
        self.assertEqual(expected, q)
