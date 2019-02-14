import argparse
import logging
import time

import requests

from data_sources.ndw.endpoints import (ENDPOINTS, TRAFFICSPEED_URL,
                                        TRAVELTIME_URL)
from data_sources.ndw.models import TrafficSpeedRaw, TravelTimeRaw
from data_sources.slurper_class import Slurper

logging.basicConfig(level=logging.DEBUG, format='%(message)s')
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
logging.getLogger("urllib3").setLevel(logging.DEBUG)


class TravelTimeSlurper(Slurper):
    model = TravelTimeRaw
    url = TRAVELTIME_URL

    def fetch(self):
        response = requests.get(TRAVELTIME_URL)
        return response.content


class TrafficSpeedSlurper(Slurper):
    model = TrafficSpeedRaw
    url = TRAFFICSPEED_URL

    def fetch(self):
        response = requests.get(TRAFFICSPEED_URL)
        return response.content


ENDPOINT_IMPORTER = {
    'traveltime': TravelTimeSlurper,
    'trafficspeed': TrafficSpeedSlurper
}


def main(make_engine=True):
    desc = "Scrape NDW."
    inputparser = argparse.ArgumentParser(desc)

    inputparser.add_argument(
        "--debug",
        action="store_true",
        default=False,
        help="Enable debugging"
    )

    inputparser.add_argument(
        "endpoint",
        type=str,
        default="traveltime",
        choices=ENDPOINTS,
        help="Provide Endpoint to scrape",
        nargs=1,
    )
    args = inputparser.parse_args()

    start = time.time()

    if args.debug:
        log.setLevel(logging.DEBUG)

    slurper = ENDPOINT_IMPORTER[args.endpoint[0]]()

    slurper.start_import(make_engine)

    log.info("Took: %s", time.time() - start)


if __name__ == "__main__":
    main()
