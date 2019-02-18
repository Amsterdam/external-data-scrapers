import gzip
import logging
import threading
import time

import zmq
from django.contrib.gis.geos import Point
from django.test import TestCase

from apps.ov.management.commands.kv6sub import ZmqClient
# import gc
from apps.ov.models import OvRaw, OvRoutes, OvStop

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
        <ARRIVAL>
            <dataownercode>CXX</dataownercode>
            <lineplanningnumber>W069</lineplanningnumber>
            <operatingday>2019-01-24</operatingday>
            <journeynumber>87</journeynumber>
            <reinforcementnumber>0</reinforcementnumber>
            <userstopcode>03099</userstopcode>
            <passagesequencenumber>0</passagesequencenumber>
            <timestamp>2019-01-24T15:36:36+01:00</timestamp>
            <source>VEHICLE</source>
            <vehiclenumber>6741</vehiclenumber>
            <punctuality>-24</punctuality>
        </ARRIVAL>
        <DEPARTURE>
            <dataownercode>CXX</dataownercode>
            <lineplanningnumber>W043</lineplanningnumber>
            <operatingday>2019-01-24</operatingday>
            <journeynumber>37</journeynumber>
            <reinforcementnumber>0</reinforcementnumber>
            <userstopcode>54445050</userstopcode>
            <passagesequencenumber>0</passagesequencenumber>
            <timestamp>2019-01-24T15:36:40+01:00</timestamp>
            <source>VEHICLE</source>
            <vehiclenumber>6631</vehiclenumber>
            <punctuality>-20</punctuality>
        </DEPARTURE>
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


class Kv6Tests(TestCase):
    def setUp(self):
        # set dummy stations and locations
        stop = OvStop(id="05065", geo_location=Point(x=1.0, y=1.0))
        stop.save()
        route = OvRoutes(
            key="CXX:W053:35",
            route_id=1,
            service_id=1,
            trip_id=1
        )
        route.save()
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
