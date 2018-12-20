import argparse
import datetime
import logging
import time

import requests

import db_helper
from data_sources.parkeergarages import endpoints, models

logging.basicConfig(level=logging.DEBUG, format='%(message)s')
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
logging.getLogger("urllib3").setLevel(logging.DEBUG)

ENDPOINTS = [
    'parking_location',
    'guidance_sign'
]

ENDPOINT_URL = {
    'parking_location': endpoints.PARKING_LOCATION_URL,
    'guidance_sign': endpoints.GUIDANCE_SIGN_URL
}

ENDPOINT_MODEL = {
    'parking_location': models.ParkingLocationRaw,
    'guidance_sign': models.GuidanceSignRaw
}


def fetch_json(endpoint):
    response = requests.get(ENDPOINT_URL[endpoint])
    return response.json()


def store(data, endpoint):
    session = db_helper.session
    model = ENDPOINT_MODEL[endpoint]
    entry = model(
        scraped_at=datetime.datetime.now(),
        data=data
    )
    session.add(entry)
    session.commit()


def start_import(make_engine, endpoint):
    if make_engine:
        engine = db_helper.make_engine(section='docker')
        db_helper.set_session(engine)

    data = fetch_json(endpoint)
    store(data, endpoint)


def main(make_engine=True):
    desc = "Scrape ParkeerGarages API."
    inputparser = argparse.ArgumentParser(desc)

    inputparser.add_argument(
        "endpoint",
        type=str,
        default="parking_location",
        choices=ENDPOINTS,
        help="Provide Endpoint to scrape",
        nargs=1,
    )

    inputparser.add_argument(
        "--debug", action="store_true", default=False, help="Enable debugging"
    )

    args = inputparser.parse_args()

    if args.debug:
        log.setLevel(logging.DEBUG)

    start = time.time()
    start_import(make_engine=make_engine, endpoint=args.endpoint[0])
    log.info("Took: %s", time.time() - start)


if __name__ == "__main__":
    main()
