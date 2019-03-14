import argparse
import gzip
import io
import logging
import time
from collections import defaultdict
from xml.etree import ElementTree
from zipfile import ZipFile

import requests
import shapefile
from bs4 import BeautifulSoup
from shapely.geometry import LineString, Point

import db_helper
from data_sources.importer_class import Importer
from data_sources.ndw.endpoints import ENDPOINTS, ROOT_URL
from data_sources.ndw.models import TrafficSpeedRaw, TravelTimeRaw
from data_sources.ndw.sql_queries import (INSERT_TRAFFICSPEED,
                                          INSERT_TRAVELTIME,
                                          SELECT_BUURT_CODE_4326,
                                          SELECT_BUURT_CODE_28992,
                                          SELECT_STADSDEEL_4326,
                                          SELECT_STADSDEEL_28992)

log = logging.getLogger(__name__)


def fetch_shapefile():
    page = requests.get(ROOT_URL).text
    soup = BeautifulSoup(page, 'html.parser')
    shapefile_url = [
        node.get('href') for node in soup.find_all('a') if 'NDW_Shapefile' in node.get('href')
    ]
    try:
        response = requests.get(ROOT_URL + '/' + shapefile_url[0])
        return response.content

    except Exception as e:
        raise Exception(f'Failed to retrieve shapefile with the following error: {e}')


class TravelTimeImporter(Importer):
    raw_model = TravelTimeRaw
    clean_model = 'importer_traveltime'
    stadsdeel_query = SELECT_STADSDEEL_4326
    buurt_code_query = SELECT_BUURT_CODE_4326

    link_areas = True
    sf_records = {}

    def start_import(self, *args, **kwargs):
        if self.link_areas:
            self.sf_records = self.get_shapefile_records()
        return super().start_import(*args, **kwargs)

    def store(self, raw_data):
        traveltime_list = []

        for row in raw_data:
            xml_file = gzip.GzipFile(fileobj=io.BytesIO(row.data), mode='rb')
            tree = ElementTree.parse(xml_file)
            root = tree.getroot()
            xml_file.close()

            ns = {'def': 'http://datex2.eu/schema/2/2_0'}

            measurements = root.iter(
                '{http://datex2.eu/schema/2/2_0}siteMeasurements'
            )

            for m in measurements:
                api_id = m.find('def:measurementSiteReference', ns).attrib['id']
                timestamp = m.find('def:measurementTimeDefault', ns).text

                trvt = m.find('def:measuredValue', ns)\
                        .find('def:measuredValue', ns)\
                        .find('def:basicData', ns)\
                        .find('def:travelTime', ns)

                duration = float(trvt.find('def:duration', ns).text)

                data_error = trvt.find('def:dataError', ns)
                data_error = (
                    data_error.text == 'true' if data_error is not None else False
                )

                computational_method = trvt.attrib.get('computationalMethod')

                supplier_calculated_data_quality = float(trvt.attrib.get('supplierCalculatedDataQuality', -1))
                standard_deviation = float(trvt.attrib.get('standardDeviation', -1))
                number_of_incomplete_input = int(trvt.attrib.get('numberOfIncompleteInputs', -1))
                number_of_input_values_used = int(trvt.attrib.get('numberOfInputValuesUsed', -1))

                geometrie, length, stadsdeel, buurt_code = self.sf_records.get(api_id, (None, None, None, None))
                # geometrie, length = None, None

                traveltime = (
                    api_id,
                    computational_method,
                    number_of_incomplete_input,
                    number_of_input_values_used,
                    standard_deviation,
                    supplier_calculated_data_quality,
                    duration,
                    data_error,
                    timestamp,
                    geometrie,
                    length,
                    stadsdeel,
                    buurt_code,
                    str(row.scraped_at)
                )
                traveltime_list.append(str(traveltime).replace('None', 'null'))

        session = db_helper.session
        log.info("Storing {} TravelTime entries".format(len(traveltime_list)))
        session.execute(INSERT_TRAVELTIME.format(', '.join(traveltime_list)))
        session.commit()
        session.close()

    def get_shapefile_reader(self):
        zipfile = ZipFile(io.BytesIO(fetch_shapefile()), 'r')
        shp = [fn for fn in zipfile.namelist() if fn.endswith('Meetvakken.shp')][0]
        dbf = [fn for fn in zipfile.namelist() if fn.endswith('Meetvakken.dbf')][0]
        return shapefile.Reader(
            shp=zipfile.open(shp),
            dbf=zipfile.open(dbf)
        )

    def get_shapefile_records(self):
        log.info("Retrieving shapefile..")
        sf = self.get_shapefile_reader()

        log.info("Populating records..")

        records = {}
        start = time.time()
        for sr in sf.iterShapeRecords():
            id = sr.record.as_dict().get('dgl_loc')
            linestring = self.linestring_to_str('4326', sr.shape.points)
            length = sr.record.as_dict().get('lengte')
            sh = LineString(sr.shape.__geo_interface__['coordinates'])

            records[id] = (linestring, length, self.get_stadsdeel(sh), self.get_buurt_code(sh))

        log.info(f"populated {len(records)} records")
        log.info("Took: %s", time.time() - start)
        return records


class TrafficSpeedImporter(Importer):
    clean_model = 'importer_trafficspeed'
    raw_model = TrafficSpeedRaw
    stadsdeel_query = SELECT_STADSDEEL_28992
    buurt_code_query = SELECT_BUURT_CODE_28992

    link_areas = True
    sf_records = {}

    def start_import(self, *args, **kwargs):
        if self.link_areas:
            self.sf_records = self.get_shapefile_records()
        return super().start_import(*args, **kwargs)

    def get_shapefile_reader(self):
        zipfile = ZipFile(io.BytesIO(fetch_shapefile()), 'r')
        shp = [fn for fn in zipfile.namelist() if fn.endswith('Telpunten.shp')][0]
        dbf = [fn for fn in zipfile.namelist() if fn.endswith('Telpunten.dbf')][0]
        shx = [fn for fn in zipfile.namelist() if fn.endswith('Telpunten.shx')][0]
        return shapefile.Reader(
            shp=zipfile.open(shp),
            dbf=zipfile.open(dbf),
            shx=zipfile.open(shx)
        )

    def get_shapefile_records(self):
        log.info("Retrieving shapefile..")
        sf = self.get_shapefile_reader()

        records = {}

        log.info("Populating records..")
        start = time.time()

        for sr in sf.iterShapeRecords():
            id = sr.record['dgl_loc']
            point = self.point_to_str('28992', sr.shape.points[0])
            sh = Point(sr.shape.__geo_interface__['coordinates'])
            records[id] = (point, self.get_stadsdeel(sh), self.get_buurt_code(sh))

        log.info(f"populated {len(records)} records")
        log.info("Took: %s", time.time() - start)
        return records

    def store(self, raw_data):
        trafficspeed_list = []

        for row in raw_data:
            xml_file = gzip.GzipFile(fileobj=io.BytesIO(row.data), mode='rb')
            tree = ElementTree.parse(xml_file)
            root = tree.getroot()
            xml_file.close()

            ns = {'def': 'http://datex2.eu/schema/2/2_0'}

            measurements = root.iter(
                '{http://datex2.eu/schema/2/2_0}siteMeasurements'
            )

            for m in measurements:
                measurement_site_reference = m.find(
                    'def:measurementSiteReference', ns
                ).attrib['id']
                measurement_time = m.find('def:measurementTimeDefault', ns).text

                for measured_value in m.findall(
                    '{http://datex2.eu/schema/2/2_0}measuredValue'
                ):
                    index = measured_value.get('index')
                    measurement_type = measured_value.find(
                        './/def:basicData', ns
                    ).items()[0][1]

                    data_error = measured_value.find('.//def:dataError', ns)

                    data_error = (
                        data_error.text == 'true' if data_error is not None else False
                    )

                    basic_data = defaultdict(lambda: None)

                    if measurement_type == 'TrafficSpeed':
                        vehiclespeed = measured_value.find('.//def:averageVehicleSpeed', ns)
                        basic_data['number_of_input_values_used'] = int(vehiclespeed.get('numberOfInputValuesUsed', 0))
                        basic_data['standard_deviation'] = float(vehiclespeed.get('standardDeviation', 0))
                        basic_data['speed'] = float(measured_value.find('.//def:speed', ns).text)

                    elif measurement_type == 'TrafficFlow':
                        basic_data['flow'] = int(measured_value.find('.//def:vehicleFlowRate', ns).text)

                    else:
                        raise Exception("Unknown type: {}".format(type))

                geometrie, stadsdeel, buurt_code = self.sf_records.get(measurement_site_reference, (None, None, None))

                trafficspeed = (
                    measurement_site_reference,
                    measurement_time,
                    measurement_type,
                    index,
                    data_error,
                    str(row.scraped_at),

                    basic_data['flow'],
                    basic_data['speed'],
                    basic_data['number_of_input_values_used'],
                    basic_data['standard_deviation'],

                    geometrie,
                    stadsdeel,
                    buurt_code,
                )

                trafficspeed_list.append(str(trafficspeed).replace('None', 'null'))

        session = db_helper.session
        log.info("Storing {} TrafficSpeed entries".format(len(trafficspeed_list)))
        session.execute(INSERT_TRAFFICSPEED.format(', '.join(trafficspeed_list)))
        session.commit()
        session.close()


ENDPOINT_IMPORTER = {
    'traveltime': TravelTimeImporter,
    'trafficspeed': TrafficSpeedImporter
}


def main(make_engine=True):
    desc = "Clean data and import into db."
    inputparser = argparse.ArgumentParser(desc)

    inputparser.add_argument(
        "endpoint",
        type=str,
        default="traveltime",
        choices=ENDPOINTS,
        help="Provide Endpoint to scrape",
        nargs=1,
    )

    inputparser.add_argument(
        "--debug",
        action="store_true",
        default=False,
        help="Enable debugging"
    )

    inputparser.add_argument(
        "--exclude_areas",
        action="store_true",
        default=False,
        help="Link areas to model"
    )

    args = inputparser.parse_args()

    if args.debug:
        log.setLevel(logging.DEBUG)

    start = time.time()

    if make_engine:
        engine = db_helper.make_engine()
        db_helper.set_session(engine)

    importer = ENDPOINT_IMPORTER[args.endpoint[0]]()

    if args.exclude_areas:
        importer.link_areas = False

    importer.start_import()

    log.info("Total time: %s", time.time() - start)


if __name__ == "__main__":
    main()
