import argparse
import calendar
import datetime
import io
import logging
import time
from xml.etree import ElementTree

from data_sources.slurper_class import Slurper
from data_sources.trafficorder.endpoints import TRAFFICORDER_URL
from data_sources.trafficorder.models import TrafficOrderRaw

logging.basicConfig(level=logging.DEBUG, format='%(message)s')
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
logging.getLogger("urllib3").setLevel(logging.DEBUG)


class TrafficOrderSlurper(Slurper):
    model = TrafficOrderRaw
    url = TRAFFICORDER_URL
    fetch_json = False

    def __init__(self, year=datetime.datetime.now().year, month=None, maximum=4020):
        self.date_query = f'''and(jaargang={year})'''

        if month:
            first, last = calendar.monthrange(year, month)
            self.date_query += f'''and(date>{year}-{month}-{first})and(date<{year}-{month}-{last})'''

        self.year = year
        self.month = month
        self.start = 1
        self.maximum = 4020

    def get_data(self, response_data, part):
        return dict(scraped_at=datetime.datetime.now(), data=response_data, part=part, year=self.year, month=self.month)

    def get_part_amount(self, response_data):
        tree = ElementTree.parse(io.BytesIO(response_data))
        root = tree.getroot()

        try:
            num_of_records = int(root.find('{http://www.loc.gov/zing/srw/}numberOfRecords').text)
        except Exception as e:
            raise Exception(f'Could not find number of records, something went wrong with the query: {e}')

        log.info(f'Total records {num_of_records}')
        parts = range(int(num_of_records / self.maximum))
        log.info(f'Amount of extra parts to fetch {(len(parts))}')
        return parts

    def get_url(self):
        return self.url.format(start=self.start, maximum=self.maximum, date_query=self.date_query)

    def start_import(self, make_engine):
        self.setup_db(make_engine)
        response_data = self.fetch()
        part_list = []
        part = 0
        part_list.append(self.get_data(response_data, part=part))

        for _ in self.get_part_amount(response_data):
            self.start += self.maximum
            part += 1
            part_list.append(self.get_data(self.fetch(), part=part))

        log.info('Storing')

        for part in part_list:
            self.store(part)


def main(make_engine=True):
    desc = "Scrape TrafficOrder."
    inputparser = argparse.ArgumentParser(desc)

    inputparser.add_argument('--year', type=int, action='store', required=True)
    inputparser.add_argument('--month', type=int, action='store')

    args = inputparser.parse_args()

    start = time.time()

    TrafficOrderSlurper(year=args.year, month=args.month).start_import(make_engine)

    log.info("Took: %s", time.time() - start)


if __name__ == "__main__":
    main()
