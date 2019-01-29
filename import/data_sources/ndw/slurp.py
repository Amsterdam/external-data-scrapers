import argparse
import logging
import time

import requests

from data_sources.ndw.endpoints import NDW_URL
from data_sources.ndw.models import TravelTimeRaw
from data_sources.slurper_class import Slurper

logging.basicConfig(level=logging.DEBUG, format='%(message)s')
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
logging.getLogger("urllib3").setLevel(logging.DEBUG)


class NDWSlurper(Slurper):
    model = TravelTimeRaw
    url = NDW_URL

    def fetch(self):
        response = requests.get(NDW_URL)
        return response.content


def main(make_engine=True):
    desc = "Scrape NDW."
    inputparser = argparse.ArgumentParser(desc)

    inputparser.add_argument(
        "--debug",
        action="store_true",
        default=False,
        help="Enable debugging"
    )

    args = inputparser.parse_args()

    start = time.time()

    if args.debug:
        log.setLevel(logging.DEBUG)

    NDWSlurper().start_import(make_engine)

    log.info("Took: %s", time.time() - start)


if __name__ == "__main__":
    main()
