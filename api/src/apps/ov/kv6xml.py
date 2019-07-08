import logging
import xml.etree.ElementTree as ET
from datetime import timedelta

from dateutil.parser import parse
from django.contrib.gis.geos import Point
from django.db import models
from django.utils import timezone

from apps.ov.bulk_inserter import bulk_inserter
from apps.ov.models import OvKv6, OvRoutes, OvRouteSection, OvStop

logging.basicConfig(level=logging.DEBUG, format='%(message)s')
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
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
        self.routes = set()
        # dict(route:stopcode, distance from last stop, prev stop)
        self.distances = {}
        # dict(route, dict(stopcode, last time))
        self.journeys = {}

    def refresh_data(self):
        log.info('removing inactive journeys')
        self.remove_inactive_journeys()
        log.info('refreshing stops and trips data')
        tmp_stops = dict(OvStop.objects.values_list('id', 'geo_location'))
        if tmp_stops:
            self.stops = tmp_stops

        tmp_routes = set(OvRoutes.objects.values_list('key', flat=True))
        if tmp_routes:
            self.routes = tmp_routes
            # clear tracked journeys
            self.journeys = {}

        prev_route = None
        prev_stop = None
        prev_dist = None
        for sect in OvRouteSection.objects.all().order_by('route_id', 'stop_sequence'):
            if not prev_route or prev_route != sect.route_id:
                # new route
                prev_route = sect.route_id
                prev_stop = sect.stop_code
                prev_dist = sect.shape_dist_traveled

            # route_id format: 'dataownercode:line:journey'
            key = f'{sect.route_id}:{sect.stop_code}'
            self.distances[key] = (sect.shape_dist_traveled - prev_dist, prev_stop)
            prev_route = sect.route_id
            prev_stop = sect.stop_code
            prev_dist = sect.shape_dist_traveled

        log.info('refreshing stops and trips data completed')
        log.info(f'{len(self.stops)} {len(self.routes)} {len(self.distances)}')

    def make_key(self, dataowner, line, journey):
        return f'{dataowner}:{line}:{journey}'

    def is_first_stop(self, dataowner, line, journey, stop):
        key = f'{self.make_key(dataowner, line, journey)}:{stop}'
        if key in self.distances:
            return self.distances[key][1] == stop
        return False

    def get_prev_dist_stop(self, dataowner, line, journey, stop):
        key = f'{self.make_key(dataowner, line, journey)}:{stop}'
        if key in self.distances:
            return self.distances[key]
        return (None, None)

    def store_arrival(self, dataowner, line, journey, stop, deptime):
        key = self.make_key(dataowner, line, journey)
        if key not in self.journeys:
            self.journeys[key] = {}
        subdict = self.journeys[key]
        subdict[stop] = deptime

    def get_arrival(self, dataowner, line, journey, stop):
        key = self.make_key(dataowner, line, journey)
        if key in self.journeys:
            subdict = self.journeys[key]
            if stop in subdict:
                return subdict[stop]
        return None

    def remove_inactive_journeys(self):
        if self.journeys:
            # make copy of keys since we are going to remove elements
            keys = self.journeys.keys()
            for key in keys:
                subdict = self.journeys[key]
                m = max(subdict.values())

                # no update on this route for more than a day, remove it
                if m and m + timedelta(days=1) <= timezone.now():
                    del self.journeys[key]

    def remove_journey(self, dataowner, line, journey):
        key = self.make_key(dataowner, line, journey)
        if key in self.journeys:
            del self.journeys[key]

    def is_ams_route(self, dataowner, line, journey):
        key = self.make_key(dataowner, line, journey)
        return key in self.routes

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

    def augment_geolocation(self, rec):
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

    def augment(self, rec):
        self.augment_geolocation(rec)

        if rec.messagetype == 'DEPARTURE' and self.is_first_stop(
                rec.dataownercode,
                rec.lineplanningnumber,
                rec.journeynumber,
                rec.userstopcode):

            # store departure as arrival for first stop
            self.store_arrival(rec.dataownercode,
                               rec.lineplanningnumber,
                               rec.journeynumber,
                               rec.userstopcode,
                               parse(rec.vehicle))

        elif rec.messagetype == 'ARRIVAL' and not self.is_first_stop(
                rec.dataownercode,
                rec.lineplanningnumber,
                rec.journeynumber,
                rec.userstopcode):

            # store own arrival if we are not the first stop
            parsed_arrival = parse(rec.vehicle)
            self.store_arrival(rec.dataownercode,
                               rec.lineplanningnumber,
                               rec.journeynumber,
                               rec.userstopcode,
                               parsed_arrival)

            # get distance since distance since last stop
            (dist, stop) = self.get_prev_dist_stop(rec.dataownercode,
                                                   rec.lineplanningnumber,
                                                   rec.journeynumber,
                                                   rec.userstopcode)
            if dist and stop:
                rec.prev_userstopcode = stop
                if stop in self.stops:
                    rec.prev_geo_location = self.stops[stop]
                # get last arrival time from prev stop
                prev_arrival = self.get_arrival(rec.dataownercode,
                                                rec.lineplanningnumber,
                                                rec.journeynumber,
                                                stop)
                if prev_arrival:
                    # calculate avg speed over last section
                    delta = (parsed_arrival - prev_arrival).total_seconds()
                    if delta > 0:
                        rec.distance = dist
                        rec.time = delta
                        # print(f'{dist/delta} = {dist} / {delta}')
        # journey ended, remove from cache
        elif rec.messagetype == 'END':
            self.remove_journey(rec.dataownercode,
                                rec.lineplanningnumber,
                                rec.journeynumber)

    def process(self, received_time, xml):
        try:
            tree = ET.ElementTree(ET.fromstring(xml))
            root = tree.getroot()
            timestamp = root.find('tmi8:Timestamp', NS)
            if timestamp is None:
                log.info(f'Skipping invalid xml {xml}')
                log.info(f'Size of cache: {len(self.journeys)}')
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
                    # check if we need to include the route
                    if not self.is_ams_route(record.dataownercode,
                                             record.lineplanningnumber,
                                             record.journeynumber):
                        continue
                    self.augment(record)
                    self.inserter.add(record)
        except Exception as e:
            log.error(e)
