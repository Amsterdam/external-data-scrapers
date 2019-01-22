# pylint:disable=E1101
# pylint: disable=unbalanced-tuple-unpacking
import zmq
import gzip
import time
import logging
from django.core.management.base import BaseCommand
from apps.ov.models import OvRaw

logging.basicConfig(level=logging.DEBUG, format='%(message)s')
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
KV6KEY = "KV6posinfo"
PUBLISHER = "tcp://pubsub.besteffort.ndovloket.nl:7658"
# PUBLISHER = "tcp://localhost:7658"
TIMEOUTMS = 60 * 1000


class KV6Client(object):
    def __init__(self):
        self.context = zmq.Context()
        self.sock = None

    def __del__(self):
        if self.context is not None:
            self.context.term()

    def subscribe(self):
        try:
            self.sock = self.context.socket(zmq.SUB)
            log.info(f'Subscribing to {PUBLISHER}')
            self.sock.connect(PUBLISHER)
            self.sock.setsockopt(zmq.RCVTIMEO, 2 * TIMEOUTMS)
            self.sock.setsockopt_string(zmq.SUBSCRIBE, "")
            return True
        except Exception as err:
            log.error(err)
            return False

    def message_loop(self):
        while True:
            try:
                [envelop, contents] = self.sock.recv_multipart()
                envelop = envelop.decode('utf-8')
                # contents is transferred as gzipped uni code
                log.info(f'{envelop} received')
                if KV6KEY in envelop:
                    record = OvRaw(feed=envelop, xml=contents)
                    record.save()
                else:
                    log.info(f'Skipping envelop {envelop}')
            # Timed out, close connection and try to reconnect.
            # (network could have been interrupted)
            except zmq.error.Again:
                if self.sock is not None:
                    self.sock.close()
                break
            except Exception as err:
                log.error(err)

    def subscribe_and_process(self):
        while True:
            if self.subscribe():
                self.message_loop()
                log.info('Timed out, trying to reconnect...')
            else:
                log.info(f'Connection failed, sleeping {0.5 * TIMEOUTMS} (ms)')
                time.sleep(0.5 * TIMEOUTMS)


class Command(BaseCommand):
    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        client = KV6Client()
        client.subscribe_and_process()
