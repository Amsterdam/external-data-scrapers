import argparse
import datetime
import gzip
import io
import logging
import time
import xml.etree.ElementTree as ET

import db_helper
import settings
from data_sources.latest_query import get_latest_query
# from data_sources.link_areas import link_areas
from data_sources.ndw.models import ThirdpartyTravelTimeRaw, TravelTimeRaw

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

            computational_method = trvt.attrib.get(
                'computationalMethod', 'null'
            )
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
            traveltime_list.append(str(traveltime))

    session = db_helper.session
    log.info("Storing {} TravelTime entries".format(len(traveltime_list)))
    session.execute(INSERT_TRAVELTIME.format(', '.join(traveltime_list)))
    session.commit()
    session.close()


def store_thirdparty(raw_data):
    session = db_helper.session

    traveltime_list = []
    for row in raw_data:
        for route in row.data['features']:
            geometrie = make_geometrie(route['geometry']['coordinates'])
            props = route['properties']

            traveltime = (
                props['Id'],
                props['Name'],
                props['Type'],
                props['Timestamp'],
                props['Length'],
                geometrie,
                str(row.scraped_at)
            )
            traveltime_list.append(str(traveltime))

    log.info("Storing {} TravelTime entries".format(len(traveltime_list)))
    session.execute(
        INSERT_THIRDPARTY_TRAVELTIME.format(', '.join(traveltime_list))
    )
    session.commit()
    session.close()


def start_import(store_func, raw_model, clean_model):
    """
    Importing the data is done in batches to avoid
    straining the resources.
    """
    session = db_helper.session
    query = get_latest_query(
        session, raw_model, clean_model
    )
    run = True

    offset = 0
    limit = settings.DATABASE_IMPORT_LIMIT

    while run:
        raw_data = query.offset(offset).limit(limit).all()
        if raw_data:
            log.info("Fetched {} raw TravelTime entries".format(len(raw_data)))
            store_func(raw_data)
            offset += limit
        else:
            run = False


INSERT_THIRDPARTY_TRAVELTIME = """
INSERT INTO importer_thirdparty_traveltime (
    measurement_site_reference,
    name,
    type,
    timestamp,
    length,
    geometrie,
    scraped_at
)
VALUES {}
"""

INSERT_TRAVELTIME = """
INSERT INTO importer_traveltime (
measurement_site_reference, computational_method, number_of_incomplete_input,
number_of_input_values_used, standard_deviation,
supplier_calculated_data_quality, duration, data_error,
measurement_time, scraped_at
)
VALUES {}
"""


def main(make_engine=True):
    desc = "Clean data and import into db."
    inputparser = argparse.ArgumentParser(desc)

    inputparser.add_argument(
        "--ndw",
        action="store_true",
        default=False,
        help="Slurp ndw"
    )

    inputparser.add_argument(
        "--thirdparty",
        action="store_true",
        default=False,
        help="Slurp thirdparty"
    )

    args = inputparser.parse_args()

    start = time.time()

    if make_engine:
        engine = db_helper.make_engine()
        db_helper.set_session(engine)

    if args.ndw:
        start_import(
            store_ndw,
            TravelTimeRaw,
            "importer_traveltime"
        )

    elif args.thirdparty:
        start_import(
            store_thirdparty,
            ThirdpartyTravelTimeRaw,
            "importer_thirdparty_traveltime"
        )

    log.info("Took: %s", time.time() - start)


if __name__ == "__main__":
    main()
