import logging
import xml.etree.ElementTree as ET

from django.contrib.gis.geos import Point
from django.db import models

from apps.ov.bulk_inserter import bulk_inserter
from apps.ov.models import OvKv6, OvStop

logging.basicConfig(level=logging.DEBUG, format='%(message)s')
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
NS = {'tmi8': 'http://bison.connekt.nl/tmi8/kv6/msg'}
KV6KEY = '{' + NS['tmi8'] + '}' + 'KV6posinfo'


class Kv6XMLProcessor(object):
    def __init__(self):
        # define override for tags
        # timestamp should map to vehicle
        self.overrides = {
            'timestamp': 'vehicle',
            'rd-x': 'rd_x',
            'rd-y': 'rd_y',
        }
        self.inserter = bulk_inserter(table=OvKv6, batch_size=10)
        self.stops = {}

    def refresh_stops(self):
        tmp = {}
        for stop in OvStop.objects.all():
            tmp[stop.id] = stop.geo_location
        if len(tmp) > 0:
            self.stops = tmp

    def strip_ns(self, xmltag):
        try:
            return xmltag.split('}', 1)[1]
        except Exception:
            return xmltag

    def set_if_exists(self, model, node):
        try:
            field_name = self.strip_ns(node.tag)
            if field_name in self.overrides:
                field_name = self.overrides[field_name]

            field = model._meta.get_field(field_name)
            setattr(model, field.attname, node.text)
        except models.FieldDoesNotExist:
            pass

    def augment(self, rec):
        # convert rd_x and rd_y to geo location if present
        # coordinates should be > 0 for NL.
        # see https://nl.wikipedia.org/wiki/Rijksdriehoeksco%C3%B6rdinaten
        valid_geo = False
        if rec.rd_x is not None and rec.rd_y is not None:
            x = float(rec.rd_x)
            y = float(rec.rd_y)
            if x >= 0 and y >= 0:
                valid_geo = True
                rec.geo_location = Point(x=x, y=y, srid=28992)
        if not valid_geo and rec.userstopcode in self.stops:
            # add station location otherwise
            rec.geo_location = self.stops[rec.userstopcode]

    def process(self, received_time, xml):
        try:
            tree = ET.ElementTree(ET.fromstring(xml))
            root = tree.getroot()
            timestamp = root.find('tmi8:Timestamp', NS)
            if timestamp is None:
                log.info(f'Skipping invalid xml {xml}')
                return
            message_time = timestamp.text

            for child in root.iter(KV6KEY):
                for event in child:
                    eventag = self.strip_ns(event.tag)
                    record = OvKv6(receive=received_time, message=message_time,
                                   messagetype=eventag)
                    # map record fields with event data on name/tag
                    for eventdata in event:
                        self.set_if_exists(record, eventdata)
                    # delay msg don't have user stop
                    if record.userstopcode and\
                       record.userstopcode not in self.stops:
                        continue
                    self.augment(record)
                    self.inserter.add(record)
        except Exception as e:
            log.error(e)
