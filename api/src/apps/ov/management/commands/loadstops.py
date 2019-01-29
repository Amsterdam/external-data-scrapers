import csv
import logging

from django.contrib.gis.geos import Point
from django.core.management.base import BaseCommand

from apps.ov.models import OvStop

logging.basicConfig(level=logging.DEBUG, format='%(message)s')
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


class Importer(object):
    def __init__(self, csv_file):
        # upper left corner, lower right corner box around ams
        self.BBOX = [52.455636, 4.714153, 52.256733, 5.070706]
        self.file = csv_file

    def in_bbox(self, lat, lon):
        return self.BBOX[0] >= lat and\
            self.BBOX[2] <= lat and\
            self.BBOX[1] <= lon and\
            self.BBOX[3] >= lon

    def import_csv(self):
        with open(self.file) as f:
            reader = csv.reader(f, delimiter=',', quotechar='"')
            # prevent duplicate stop codes within one transaction
            processed_stops = set()
            next(reader, None)  # skip the headers
            # stop_id, stop_code, stop_name, stop_lat, stop_lon
            for row in reader:
                stopcode = row[1]
                if not stopcode or stopcode in processed_stops:
                    continue
                processed_stops.add(stopcode)
                lat = float(row[3])
                lon = float(row[4])
                if not self.in_bbox(lat, lon):
                    continue
                stopname = row[2]
                geo = Point(x=lon, y=lat)
                log.info(f'{stopcode} {stopname} lon: {lon} lat: {lat}')
                OvStop.objects.update_or_create(
                    id=stopcode,
                    name=stopname,
                    geo_location=geo
                )


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('csv', type=str)

    def handle(self, *args, **options):
        importer = Importer(options['csv'])
        importer.import_csv()
