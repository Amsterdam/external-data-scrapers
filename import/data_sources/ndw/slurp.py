import argparse
import logging
import time

import requests

from data_sources.ndw.endpoints import NDW_URL, THIRDPARTY_URL
from data_sources.ndw.models import ThirdpartyTravelTimeRaw, TravelTimeRaw
from data_sources.slurper_class import Slurper

logging.basicConfig(level=logging.DEBUG, format='%(message)s')
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
logging.getLogger("urllib3").setLevel(logging.DEBUG)


class ThirdPartyNDWSlurper(Slurper):
    model = ThirdpartyTravelTimeRaw
    url = THIRDPARTY_URL


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

    if args.debug:
        log.setLevel(logging.DEBUG)

    if args.ndw:
        NDWSlurper().start_import(make_engine)

    elif args.thirdparty:
        ThirdPartyNDWSlurper().start_import(make_engine)

    else:
        raise Exception("No arguments given")

    log.info("Took: %s", time.time() - start)


if __name__ == "__main__":
    main()
