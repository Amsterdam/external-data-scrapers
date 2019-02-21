import argparse
import datetime
import logging
import time

import db_helper
from data_sources.ndw.endpoints import ENDPOINTS
from data_sources.ndw.sql_queries import (INSERT_DAILY_TRAFFICSPEED_SUMMARY,
                                          INSERT_DAILY_TRAVELTIME_SUMMARY,
                                          SCRAPED_AT_WHERE_CLAUSE)

log = logging.getLogger(__name__)


def summarize(all_flag, insert_query):
    session = db_helper.session
    where_clause = SCRAPED_AT_WHERE_CLAUSE.format(datetime.datetime.today().strftime("%Y-%m-%d"))
    if all_flag:
        where_clause = ''

    session.execute(insert_query.format(where_clause))
    session.commit()


ENDPOINT_DAILY_INSERT_QUERY = {
    'traveltime': INSERT_DAILY_TRAVELTIME_SUMMARY,
    'trafficspeed': INSERT_DAILY_TRAFFICSPEED_SUMMARY
}


def main(make_engine=True):
    desc = "Clean data and import into db."

    inputparser = argparse.ArgumentParser(desc)

    inputparser.add_argument(
        "--all",
        action="store_true",
        default=False,
        help="Summarize everything"
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

    if make_engine:
        engine = db_helper.make_engine()
        db_helper.set_session(engine)

    args = inputparser.parse_args()

    summarize(args.all, ENDPOINT_DAILY_INSERT_QUERY[args.endpoint[0]])

    log.info("Total time: %s", time.time() - start)


if __name__ == "__main__":
    main()
