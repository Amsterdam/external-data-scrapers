# pylint:disable=E1101
# pylint: disable=unbalanced-tuple-unpacking
import gzip
import logging
import time
from datetime import datetime, timedelta

from dateutil.tz import tzlocal
from django.core.management.base import BaseCommand
from django.db import connection

from apps.ov.bulk_inserter import bulk_inserter
from apps.ov.kv6xml import Kv6XMLProcessor
from apps.ov.models import OvRaw
from apps.ov.zmq_poller import ZmqPoller
from apps.ov.zmq_subscriber import ZmqSubscriber

logging.basicConfig(level=logging.DEBUG, format='%(message)s')
log = logging.getLogger(__name__)
log.setLevel(logging.ERROR)
KV6KEY = "KV6posinfo"
PUBLISHER = "tcp://pubsub.besteffort.ndovloket.nl:7658"
TIMEOUTMS = 60


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
            now = datetime.now(tzlocal())
            self.xmlprocessor.process(now, unpacked)
        else:
            log.info(f'Skipping envelop {envelop}')


class ZmqClient(object):
    def __init__(self, publisher=PUBLISHER):
        self.stop = False
        self.publisher = publisher
        self.poller = ZmqPoller()
        # Add addition subscribers to the list
        self.subscribers = [KV6Subscriber(self.publisher)]
        self.next_refresh = None

    def subscribe(self):
        try:
            for sub in self.subscribers:
                sub.connect()
                self.poller.register(sub)
            return True
        except Exception as err:
            log.error(err)
            return False

    def check_refresh(self):
        if self.next_refresh is None or self.next_refresh <= datetime.now():
            for sub in self.subscribers:
                sub.handle_refreshdata()
            self.next_refresh = datetime.now() + timedelta(days=1)

    def message_loop(self):
        while True:
            try:
                self.check_refresh()
                if self.stop:
                    # we need to close the connection within the
                    # thread, else it will be kept alive
                    connection.close()
                    log.info('Stop: Terminating message loop')
                    break
                for subscr in self.poller.poll():
                    subscr.handle_message()
            except Exception as err:
                log.error(err)

    def subscribe_and_process(self):
        while True:
            if self.subscribe():
                self.message_loop()
                log.info('Timed out, trying to reconnect...')
            else:
                log.info(f'Connection failed, sleeping {0.5 * TIMEOUTMS} (ms)')
            if self.stop:
                connection.close()
                log.info('Stop: Terminating pubsub')
                break
            time.sleep(0.5 * TIMEOUTMS)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('url', type=str, nargs='?')

    def handle(self, *args, **options):
        addr = None if 'url' not in options else options['url']
        client = ZmqClient() if addr is None else ZmqClient(addr)
        client.subscribe_and_process()
