import gzip
import logging

from django.core.management.base import BaseCommand

from apps.ov.kv6xml import Kv6XMLProcessor
from apps.ov.models import OvRaw

logging.basicConfig(level=logging.DEBUG, format='%(message)s')
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


class Command(BaseCommand):
    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        proc = Kv6XMLProcessor()
        for kv6 in OvRaw.objects.all():
            proc.process(kv6.created, gzip.decompress(kv6.xml).decode('utf-8'))
