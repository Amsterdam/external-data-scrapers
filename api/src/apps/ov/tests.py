from django.test import TestCase
import zmq
import time
import gzip
import threading
import logging
# import gc
from apps.ov.models import OvRaw
from apps.ov.management.commands.kv6sub import KV6Client
# Create your tests here.
PORT = 9999
ADDR = f'tcp://127.0.0.1:{PORT}'
TOPIC = b'/GVB/KV6posinfo'
XML = b'<xml><data>test</data></xml>'

logging.basicConfig(level=logging.DEBUG, format='%(message)s')
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


class MockZmqServer(object):
    def __init__(self):
        self.stop = False
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PUB)
        self.socket.bind(ADDR)

    def start_thread(self):
        self.thread = threading.Thread(target=self.run, args=())
        self.thread.daemon = True
        self.thread.start()

    def run(self):
        while True:
            if self.stop:
                break
            data = [TOPIC, gzip.compress(XML)]
            self.socket.send_multipart(data)
            time.sleep(0.05)
        log.info('Server exit')

    def request_term(self):
        self.stop = True
        self.thread.join()
        self.socket.close()
        self.context.term()
        log.info('server thread finished')


class MockKv6Client(object):
    def __init__(self):
        self.worker = None

    def start_thread(self):
        self.thread = threading.Thread(target=self.run, args=())
        self.thread.daemon = True
        self.thread.start()

    def run(self):
        self.worker = KV6Client(publisher=ADDR)
        self.worker.subscribe_and_process()
        log.info('Client exit')

    def request_term(self):
        self.worker.stop = True
        self.thread.join()
        log.info('client thread finished')


class Kv6Tests(TestCase):
    def setUp(self):
        self.server = MockZmqServer()
        self.client = MockKv6Client()

    def test_subscribe(self):
        self.server.start_thread()
        self.client.start_thread()
        time.sleep(1)
        self.client.request_term()
        self.server.request_term()
        log.info('cleanup')
        # log.info(f'{gc.get_referrers(self.client)} refs to client')
        # log.info(f'{gc.get_referrers(self.server)} refs to server')
        del self.server
        del self.client
        # we should have records in the db now
        allrecords = OvRaw.objects.all()
        count = allrecords.count()
        self.assertTrue(count > 0)
        first = allrecords[:1].get()
        decompressed = gzip.decompress(first.xml)
        self.assertEqual(decompressed, XML)
        self.assertEqual(first.feed, TOPIC.decode('utf-8'))
        log.info('done')
