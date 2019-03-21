import gzip
import logging
import threading
import time
from datetime import datetime

import zmq
from dateutil.tz import tzlocal
from django.contrib.gis.geos import Point
from django.db import connection
from django.test import TransactionTestCase

from apps.ov.bulk_inserter import bulk_inserter
from apps.ov.kv6xml import Kv6XMLProcessor
# import gc
from apps.ov.models import OvKv6, OvRaw, OvRoutes, OvRouteSection, OvStop
from apps.ov.partition_util import PartitionUtil
from apps.ov.zmq_base_client import ZmqBaseClient
from apps.ov.zmq_subscriber import ZmqSubscriber

# Create your tests here.
PORT = 9999
ADDR = f'tcp://127.0.0.1:{PORT}'
TOPIC = b'/GVB/KV6posinfo'
XML = b'''<?xml version="1.0" encoding="utf-8"?>
<VV_TM_PUSH xmlns:tmi8c="http://bison.connekt.nl/tmi8/kv6/core"
    xmlns="http://bison.connekt.nl/tmi8/kv6/msg">
    <SubscriberID>GOVI-SubscriberId</SubscriberID>
    <Version>BISON 8.1.0.0</Version>
    <DossierName>KV6posinfo</DossierName>
    <Timestamp>2019-01-24T15:36:43.0867087+01:00</Timestamp>
    <KV6posinfo>
        <OFFROUTE>
            <dataownercode>CXX</dataownercode>
            <lineplanningnumber>W053</lineplanningnumber>
            <operatingday>2019-01-24</operatingday>
            <journeynumber>35</journeynumber>
            <reinforcementnumber>0</reinforcementnumber>
            <timestamp>2019-01-24T15:36:39+01:00</timestamp>
            <source>VEHICLE</source>
            <userstopcode>05065</userstopcode>
            <passagesequencenumber>0</passagesequencenumber>
            <vehiclenumber>4962</vehiclenumber>
            <rd-x>81434</rd-x>
            <rd-y>451631</rd-y>
        </OFFROUTE>
        <DEPARTURE>
            <dataownercode>CXX</dataownercode>
            <lineplanningnumber>W053</lineplanningnumber>
            <operatingday>2019-01-24</operatingday>
            <journeynumber>35</journeynumber>
            <reinforcementnumber>0</reinforcementnumber>
            <userstopcode>stop1</userstopcode>
            <passagesequencenumber>0</passagesequencenumber>
            <timestamp>2019-01-24T15:36:40+01:00</timestamp>
            <source>VEHICLE</source>
            <vehiclenumber>6631</vehiclenumber>
            <punctuality>-20</punctuality>
        </DEPARTURE>
        <ARRIVAL>
            <dataownercode>CXX</dataownercode>
            <lineplanningnumber>W053</lineplanningnumber>
            <operatingday>2019-01-24</operatingday>
            <journeynumber>35</journeynumber>
            <reinforcementnumber>0</reinforcementnumber>
            <userstopcode>stop2</userstopcode>
            <passagesequencenumber>0</passagesequencenumber>
            <timestamp>2019-01-24T15:37:40+01:00</timestamp>
            <source>VEHICLE</source>
            <vehiclenumber>6741</vehiclenumber>
            <punctuality>-24</punctuality>
        </ARRIVAL>
        <ONROUTE>
            <dataownercode>CXX</dataownercode>
            <lineplanningnumber>W055</lineplanningnumber>
            <operatingday>2019-01-24</operatingday>
            <journeynumber>51</journeynumber>
            <reinforcementnumber>0</reinforcementnumber>
            <userstopcode>54200150</userstopcode>
            <passagesequencenumber>0</passagesequencenumber>
            <timestamp>2019-01-24T15:36:39+01:00</timestamp>
            <source>VEHICLE</source>
            <vehiclenumber>6747</vehiclenumber>
            <punctuality>70</punctuality>
            <distancesincelastuserstop>350</distancesincelastuserstop>
            <rd-x>89797</rd-x>
            <rd-y>448598</rd-y>
        </ONROUTE>
    </KV6posinfo>
</VV_TM_PUSH>
'''

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


class MockSubscriber(ZmqSubscriber):
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
        if 'KV6posinfo' in envelop:
            record = OvRaw(feed=envelop, xml=contents)
            self.inserter.add(record)
            unpacked = gzip.decompress(record.xml).decode('utf-8')
            now = datetime.now(tzlocal())
            self.xmlprocessor.process(now, unpacked)
        else:
            log.info(f'Skipping envelop {envelop}')


class ZmqClient(ZmqBaseClient):
    def __init__(self, publisher=ADDR):
        super().__init__(publisher)
        # Add additional subscribers to the list
        self.subscribers = [MockSubscriber(self.publisher)]


class MockKv6Client(object):
    def __init__(self):
        self.worker = None

    def start_thread(self):
        self.thread = threading.Thread(target=self.run, args=())
        self.thread.daemon = True
        self.thread.start()

    def run(self):
        self.worker = ZmqClient(publisher=ADDR)
        self.worker.subscribe_and_process()
        log.info('Client exit')

    def request_term(self):
        self.worker.stop = True
        self.thread.join()
        log.info('client thread finished')


class Kv6Tests(TransactionTestCase):
    def setUp(self):
        log.info('Set up mock data for tests')
        # set dummy stations and locations
        OvStop.objects.create(id="05065", stop_id=1, geo_location=Point(x=1.0, y=1.0))
        OvStop.objects.create(id="stop1", stop_id=2, geo_location=Point(x=1.0, y=2.0))
        OvStop.objects.create(id="stop2", stop_id=3, geo_location=Point(x=1.0, y=3.0))

        route = OvRoutes.objects.create(
            key="CXX:W053:35",
            route_id=1,
            service_id=1,
            trip_id=1
        )

        OvRouteSection.objects.create(
            route=route,
            stop_sequence=0,
            stop_id=2,
            stop_code='stop1',
            shape_dist_traveled=0)

        OvRouteSection.objects.create(
            route=route,
            stop_sequence=1,
            stop_id=3,
            stop_code='stop1',
            shape_dist_traveled=1000)

        pu = PartitionUtil()
        d = datetime.strptime('2019-01-24', '%Y-%m-%d').date()
        q = pu.make_partition_query(OvKv6._meta.db_table, pu.week_partition(d))
        with connection.cursor() as c:
            c.execute(q)
        log.info('Set up mock data for tests completed')
        self.server = MockZmqServer()
        self.client = MockKv6Client()

    def test_subscribe(self):
        self.server.start_thread()
        self.client.start_thread()
        time.sleep(10)
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
