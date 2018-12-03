import argparse
import datetime
import logging
import time

import requests

import db_helper
from endpoints import URL
from models import OvFietsRaw

logging.basicConfig(level=logging.DEBUG, format='%(message)s')
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
logging.getLogger("urllib3").setLevel(logging.DEBUG)


def fetch():
    response = requests.get(URL)
    return response.json()['locaties']


def store(data):
    session = db_helper.session
    ov_fiets = OvFietsRaw(
        scraped_at=datetime.datetime.now(),
        data=data
    )
    session.add(ov_fiets)
    session.commit()


def main(make_engine):
    if make_engine:
        engine = db_helper.make_engine(section='docker')
        db_helper.set_session(engine)

    data = fetch()
    store(data)


def start_import(make_engine=True):
    start = time.time()
    main(make_engine=make_engine)
    log.info("Took: %s", time.time() - start)


if __name__ == "__main__":
    desc = "Scrape OV fiets API."
    inputparser = argparse.ArgumentParser(desc)

    inputparser.add_argument(
        "--debug", action="store_true", default=False, help="Enable debugging"
    )

    args = inputparser.parse_args()
    if args.debug:
        log.setLevel(logging.DEBUG)

    start_import()
