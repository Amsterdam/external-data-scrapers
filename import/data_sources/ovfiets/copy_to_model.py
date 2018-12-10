"""Copy raw data into django api models."""

import argparse
import logging
import time
from datetime import datetime

import db_helper
from data_sources.ovfiets.models import OvFiets, OvFietsRaw

log = logging.getLogger(__name__)


def store_data(raw_data):
    session = db_helper.session

    stations = []
    for raw_stations in raw_data:
        for raw_station in raw_stations.data['locaties'].values():
            lng = raw_station.pop('lng', None)
            lat = raw_station.pop('lat', None)

            ovfiets = OvFiets(**dict(
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
            ))
            stations.append(ovfiets)

    log.info("Storing {} OvFiets entries".format(len(stations)))
    session.bulk_save_objects(stations)
    session.commit()


def get_latest_data():
    """
    Get latest raw data to according to last imported data.
    Can be moved to utils.py when more projects use it
    """
    session = db_helper.session

    latest = (
        session.query(OvFiets)
        .order_by(OvFiets.scraped_at.desc())
        .first()
    )
    if latest:
        # update since api
        return (
            session.query(OvFietsRaw)
            .order_by(OvFietsRaw.scraped_at.desc())
            .filter(OvFietsRaw.scraped_at > latest.scraped_at)
        )
    # empty api.
    return session.query(OvFietsRaw).all()


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
    raw_data = get_latest_data()
    store_data(raw_data)


def main():
    if args.link_areas:
        return link_areas(UPDATE_STADSDEEL)
    start_import()


if __name__ == "__main__":
    desc = "Clean data and import into db."
    inputparser = argparse.ArgumentParser(desc)

    inputparser.add_argument(
        "--link_areas", action="store_true",
        default=False, help="Link stations with neighbourhood areas"
    )

    args = inputparser.parse_args()

    engine = db_helper.make_engine()
    session = db_helper.set_session(engine)

    start = time.time()
    main()
    log.info("Took: %s", time.time() - start)

    session.close()
