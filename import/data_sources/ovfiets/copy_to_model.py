"""Copy raw data into django api models."""

import argparse
import logging
import time
from datetime import datetime

import db_helper
import settings
from data_sources.latest_query import get_latest_query
from data_sources.ovfiets.models import OvFiets, OvFietsRaw

log = logging.getLogger(__name__)


def store_data(raw_data):
    session = db_helper.session

    stations = []
    for raw_stations in raw_data:
        for raw_station in raw_stations.data['locaties'].values():
            lng = raw_station.pop('lng', None)
            lat = raw_station.pop('lat', None)

            ovfiets = dict(
                scraped_at=raw_stations.scraped_at,
                name=raw_station.pop('name', None),
                description=raw_station.pop('description', None),
                station_code=raw_station.pop('stationCode', None),
                open=raw_station.pop('open', None),
                geometrie=f'SRID=4326;POINT({lng} {lat})',
                location_code=raw_station['extra'].pop('locationCode', None),
                rental_bikes=raw_station['extra'].pop('rentalBikes', None),
                opening_hours=raw_station.pop('openingHours', None),

                fetch_time=datetime.fromtimestamp(
                    raw_station['extra'].pop('fetchTime', None)
                ),
                # add what is left
                unmapped=raw_station
            )
            stations.append(ovfiets)

    log.info("Storing {} OvFiets entries".format(len(stations)))
    session.bulk_insert_mappings(OvFiets, stations)
    session.commit()


UPDATE_STADSDEEL = """
UPDATE importer_ovfiets tt
SET stadsdeel = s.code
FROM (SELECT * from stadsdeel) as s
WHERE ST_DWithin(s.wkb_geometry, tt.geometrie, 0)
AND stadsdeel is null
AND tt.geometrie IS NOT NULL
"""


def link_areas(sql):
    session = db_helper.session
    session.execute(sql)
    session.commit()


def start_import():
    """
    Importing the data is done in batches to avoid
    straining the resources.
    """
    session = db_helper.session
    query = get_latest_query(session, OvFietsRaw, OvFiets)
    run = True

    offset = 0
    limit = settings.DATABASE_IMPORT_LIMIT

    while run:
        raw_data = query.offset(offset).limit(limit).all()

        if raw_data:
            log.info("Fetched {} raw OvFiets entries".format(len(raw_data)))
            store_data(raw_data)
            offset += limit
        else:
            run = False


def main(make_engine=True):
    desc = "Clean data and import into db."
    inputparser = argparse.ArgumentParser(desc)

    inputparser.add_argument(
        "--link_areas", action="store_true",
        default=False, help="Link stations with neighbourhood areas"
    )

    args = inputparser.parse_args()

    start = time.time()

    if make_engine:
        engine = db_helper.make_engine()
        db_helper.set_session(engine)

    if args.link_areas:
        link_areas(UPDATE_STADSDEEL)
    else:
        start_import()

    log.info("Took: %s", time.time() - start)
    session = db_helper.session
    session.close()


if __name__ == "__main__":
    main()
