"""Copy raw data into django api models."""

import time
import argparse
import logging
import db_helper

from datetime import datetime
from models import OvFietsRaw, OvFiets


log = logging.getLogger(__name__)


def store_data(raw_data):
    stations = []
    for raw_stations in raw_data:
        for raw_station in raw_stations.data.values():
            ovfiets = OvFiets(**dict(
                scraped_at=raw_stations.scraped_at,
                name=raw_station['name'],
                description=raw_station.get('description'),
                station_code=raw_station.get('stationCode'),
                open=raw_station['open'],
                lng=raw_station['lng'],
                lat=raw_station['lat'],
                location_code=raw_station['extra']['locationCode'],
                rental_bikes=raw_station['extra']['rentalBikes'],
                opening_hours=raw_station.get('openingHours'),

                fetch_time=datetime.fromtimestamp(
                    raw_station['extra']['fetchTime']
                ),
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


def main():
    raw_data = get_latest_data()
    store_data(raw_data)


if __name__ == "__main__":
    desc = "Clean data and import into db."
    inputparser = argparse.ArgumentParser(desc)

    args = inputparser.parse_args()

    engine = db_helper.make_engine()
    session = db_helper.set_session(engine)

    start = time.time()
    main()
    log.info("Took: %s", time.time() - start)

    session.close()
