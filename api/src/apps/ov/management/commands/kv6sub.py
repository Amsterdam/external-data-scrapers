# pylint:disable=E1101
# pylint: disable=unbalanced-tuple-unpacking
import gzip
import logging

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.ov.bulk_inserter import bulk_inserter
from apps.ov.kv6xml import Kv6XMLProcessor
from apps.ov.models import OvRaw
from apps.ov.zmq_base_client import ZmqBaseClient
from apps.ov.zmq_subscriber import ZmqSubscriber

logging.basicConfig(level=logging.DEBUG, format='%(message)s')
log = logging.getLogger(__name__)
log.setLevel(logging.ERROR)
KV6KEY = "KV6posinfo"
PUBLISHER = "tcp://pubsub.besteffort.ndovloket.nl:7658"


class KV6Subscriber(ZmqSubscriber):
    def __init__(self, url):
        self.inserter = bulk_inserter(table=OvRaw, batch_size=10)
        self.xmlprocessor = Kv6XMLProcessor()
        super().__init__(url)

    def handle_refreshdata(self):
        self.xmlprocessor.refresh_data()

    def handle_message(self):
        [envelop, contents] = self.sock.recv_multipart()
        envelop = envelop.decode('utf-8')
        # contents is transferred as gzipped uni code
        log.info(f'{envelop} received')
        if KV6KEY in envelop:
            record = OvRaw(feed=envelop, xml=contents)
            self.inserter.add(record)
            unpacked = gzip.decompress(record.xml).decode('utf-8')
            now = timezone.now()
            self.xmlprocessor.process(now, unpacked)
        else:
            log.info(f'Skipping envelop {envelop}')


class ZmqClient(ZmqBaseClient):
    def __init__(self, publisher=PUBLISHER):
        super().__init__(publisher)
        # Add additional subscribers to the list
        self.subscribers = [KV6Subscriber(self.publisher)]


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('url', type=str, nargs='?')

    def handle(self, *args, **options):
        addr = None if 'url' not in options else options['url']
        client = ZmqClient() if addr is None else ZmqClient(addr)
        client.subscribe_and_process()
