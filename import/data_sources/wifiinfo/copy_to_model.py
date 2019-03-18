import argparse
import datetime
import io
import logging
import time

from objectstore import objectstore

import db_helper
import settings
from data_sources.wifiinfo.models import TempWifiInfo
from data_sources.wifiinfo.sql_queries import INSERT_WIFIINFO

log = logging.getLogger(__name__)
logging.getLogger("urllib3").setLevel(logging.INFO)


class WifiInfoImporter:
    def __init__(self):
        self.session = db_helper.session
        self.engine = self.session.bind

    def get_os_meta_list(self):
        connection = objectstore.get_connection(settings.OBJECTSTORE_CONF)
        return objectstore.get_full_container_list(connection, 'blip_wifi')

    def get_os_file_stream(self, meta):
        file_name = meta['name']
        connection = objectstore.get_connection(settings.OBJECTSTORE_CONF)
        _object = connection.get_object("blip_wifi", file_name)
        return io.BytesIO(_object[1])

    def get_csv_list(self, os_meta_list):
        csv_list = []

        query = self.session.execute('SELECT csv_name from csvfileinfo').fetchall()
        names = next(zip(*query)) if query else []

        for file_meta in os_meta_list:
            if file_meta['name'] not in names:
                csv_list.append(file_meta)
        return csv_list

    def copy_to_temp(self, stream):
        next(stream)  # next to skip header

        engine_conn = self.engine.raw_connection()
        cursor = engine_conn.cursor()
        csv_columns = [
            'unique_id',
            'sensor',
            'first_detection',
            'last_detection',
            'strongest_signal_timestamp',
            'strongest_signal_rssi'
        ]

        cursor.copy_from(stream, 'temp_importer_wifiinfo', ',', columns=csv_columns)
        cursor.close()
        engine_conn.commit()

    def insert_to_table(self, meta):
        name = meta['name']
        log.info(f'importing {name}')
        self.session.execute(
            f"INSERT INTO csvfileinfo (csv_name, scraped_at) values ('{name}', '{datetime.datetime.now()}')"
        )
        self.session.execute(
            INSERT_WIFIINFO.format(csv_name=name)
        )
        self.session.commit()

    def start_import(self):
        os_meta_list = self.get_os_meta_list()
        csv_list = self.get_csv_list(os_meta_list)
        log.info(f'fetched {len(os_meta_list)} metadata')

        for csv_meta in csv_list:
            self.session.query(TempWifiInfo).delete()
            stream = self.get_os_file_stream(csv_meta)
            self.copy_to_temp(stream)
            self.insert_to_table(csv_meta)


def main(make_engine=True):
    desc = "Clean data and import into db."
    inputparser = argparse.ArgumentParser(desc)
    inputparser.add_argument(
        "--debug",
        action="store_true",
        default=False,
        help="Enable debugging"
    )

    args = inputparser.parse_args()

    if args.debug:
        log.setLevel(logging.DEBUG)

    start = time.time()

    if make_engine:
        engine = db_helper.make_engine()
        db_helper.set_session(engine)

    WifiInfoImporter().start_import()

    log.info("Total time: %s", time.time() - start)


if __name__ == "__main__":
    main()
