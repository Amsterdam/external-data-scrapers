import argparse
import datetime
import gzip
import io
import logging
import time
import xml.etree.ElementTree as ET
from zipfile import ZipFile

import requests
import shapefile

import db_helper
import settings
from data_sources.latest_query import get_latest_query
from data_sources.link_areas import link_areas
from data_sources.ndw.endpoints import SHAPEFILE_URL
from data_sources.ndw.models import TravelTimeRaw

log = logging.getLogger(__name__)


def make_geometrie(coordinates):
    string = ''
    for pair in coordinates:
        string += '{} {},'.format(pair[0], pair[1])
    string = string.strip(',')
    return 'SRID=4326;LINESTRING({})'.format(string)


def store_ndw(raw_data):
    traveltime_list = []

    for row in raw_data:
        xml_file = gzip.GzipFile(fileobj=io.BytesIO(row.data), mode='rb')
        tree = ET.parse(xml_file)
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
            data_error = data_error.text == 'true' if data_error else False

            computational_method = trvt.attrib.get('computationalMethod')
            supplier_calculated_data_quality = float(
                trvt.attrib.get('supplierCalculatedDataQuality', -1)
            )
            standard_deviation = float(
                trvt.attrib.get('standardDeviation', -1)
            )
            number_of_incomplete_input = int(
                trvt.attrib.get('numberOfIncompleteInputs', -1)
            )
            number_of_input_values_used = int(trvt.attrib.get(
                'numberOfInputValuesUsed', -1)
            )

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
                str(datetime.datetime.now())
            )
            traveltime_list.append(str(traveltime).replace('None', 'null'))

    session = db_helper.session
    log.info("Storing {} TravelTime entries".format(len(traveltime_list)))
    session.execute(INSERT_TRAVELTIME.format(', '.join(traveltime_list)))
    session.commit()
    session.close()


def start_import():
    """
    Importing the data is done in batches to avoid
    straining the resources.
    """
    session = db_helper.session
    query = get_latest_query(
        session, TravelTimeRaw, 'importer_traveltime'
    )
    run = True

    offset = 0
    limit = settings.DATABASE_IMPORT_LIMIT

    while run:
        raw_data = query.offset(offset).limit(limit).all()
        if raw_data:
            log.info("Fetched {} raw TravelTime entries".format(len(raw_data)))
            store_ndw(raw_data)
            offset += limit
        else:
            run = False


INSERT_TRAVELTIME = """
INSERT INTO importer_traveltime (
measurement_site_reference, computational_method, number_of_incomplete_input,
number_of_input_values_used, standard_deviation,
supplier_calculated_data_quality, duration, data_error,
measurement_time, scraped_at
)
VALUES {}
"""


def get_shapefile():
    response = requests.get(SHAPEFILE_URL)
    zipfile = ZipFile(io.BytesIO(response.content), 'r')
    date = zipfile.namelist()[0].split('_')[0]
    return shapefile.Reader(
        shp=zipfile.open(f"{date}_Meetvakken.shp"),
        dbf=zipfile.open(f"{date}_Meetvakken.dbf")
    )


def add_coordinates():
    session = db_helper.session

    log.info("Retrieving shapefile..")
    sf = get_shapefile()

    log.info("Starting update..")
    for sr in sf.iterShapeRecords():
        id = sr.record.as_dict().get('dgl_loc')
        linestring = make_geometrie(sr.shape.points)
        session.execute(
            f"""
            UPDATE importer_traveltime
            set geometrie='{linestring}'
            where measurement_site_reference='{id}';
            """
        )
    log.info("Commiting to db..")
    session.commit()
    log.info("done")


def main(make_engine=True):
    desc = "Clean data and import into db."
    inputparser = argparse.ArgumentParser(desc)

    inputparser.add_argument(
        "--debug",
        action="store_true",
        default=False,
        help="Enable debugging"
    )

    inputparser.add_argument(
        "--link_shapefile",
        action="store_true",
        default=False,
        help="Link shapefile coordinates to model"
    )

    inputparser.add_argument(
        "--link_areas",
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

    start_import()
    session = db_helper.session

    if args.link_shapefile:
        add_coordinates()
    elif args.link_areas:
        link_areas(session, "importer_traveltime")
    else:
        start_import()

    log.info("Took: %s", time.time() - start)


if __name__ == "__main__":
    main()
