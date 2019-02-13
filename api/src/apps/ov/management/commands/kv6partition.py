import logging

from dateutil import relativedelta
from django.core.management.base import BaseCommand
from django.db import connection

from apps.ov.models import OvKv6
from apps.ov.partition_util import PartitionUtil

logging.basicConfig(level=logging.DEBUG, format='%(message)s')
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
PARTITIONS_TO_ADD = 4


class Command(BaseCommand):
    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        p = PartitionUtil()
        qs = []
        for i in range(PARTITIONS_TO_ADD):
            d = p.today() + relativedelta.relativedelta(weeks=i)
            q = p.make_partition_query(
                OvKv6._meta.db_table,
                p.week_partition(d)
            )
            log.info(q)
            qs.append(q)
        if qs:
            with connection.cursor() as c:
                for q in qs:
                    c.execute(q)
