import argparse
import datetime
import logging
import time

import requests

import db_helper
from data_sources.ndw.endpoints import URL
from data_sources.ndw.models import TravelTimeRaw

logging.basicConfig(level=logging.DEBUG, format='%(message)s')
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
logging.getLogger("urllib3").setLevel(logging.DEBUG)


def fetch_json():
    response = requests.get(URL)
    return response.json()


def store(data):
    session = db_helper.session
    traveltime = TravelTimeRaw(
        scraped_at=datetime.datetime.now(),
        data=data
    )
    session.add(traveltime)
    session.commit()


def start_import(make_engine):
    if make_engine:
        engine = db_helper.make_engine(section='docker')
        db_helper.set_session(engine)

    data = fetch_json()
    store(data)


def main(make_engine=True):
    desc = "Scrape ndw API."
    inputparser = argparse.ArgumentParser(desc)

    inputparser.add_argument(
        "--debug", action="store_true", default=False, help="Enable debugging"
    )

    args = inputparser.parse_args()

    if args.debug:
        log.setLevel(logging.DEBUG)

    start = time.time()
    start_import(make_engine=make_engine)
    log.info("Took: %s", time.time() - start)
    session = db_helper.session
    session.close()


if __name__ == "__main__":
    main()
