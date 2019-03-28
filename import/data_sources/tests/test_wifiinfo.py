import logging
import unittest
from unittest.mock import patch

import db_helper
from data_sources.wifiinfo import copy_to_model, models
from settings import BASE_DIR, TESTING

log = logging.getLogger(__name__)

FIXTURE_PATH = BASE_DIR + "/data_sources/fixtures"

transaction = []
connection = []
engine = []
session = []


def setup_module():
    global transaction, connection, engine, session
    TESTING["running"] = True
    db_helper.create_db()
    engine = db_helper.make_engine(section="test")
    connection = engine.connect()
    transaction = connection.begin()
    session = db_helper.set_session(engine)
    session.execute("CREATE EXTENSION IF NOT EXISTS postgis;")
    session.commit()
    models.Base.metadata.drop_all(bind=engine)
    models.Base.metadata.create_all(bind=engine)


def teardown_module():
    global transaction, connection, engine, session
    transaction.rollback()
    session.close()
    engine.dispose()
    connection.close()
    db_helper.drop_db()
    TESTING["running"] = False


class ArgumentParser:
    debug = True

    def __init__(self, **kwargs):
        for name in kwargs:
            setattr(self, name, kwargs[name])


@patch("data_sources.trafficorder.slurp.argparse.ArgumentParser.parse_args")
class TestCopyWifiInfo(unittest.TestCase):
    """Test writing to database."""

    def setUp(self):
        global engine
        models.Base.metadata.create_all(bind=engine)

    def tearDown(self):
        global engine
        session.close()
        models.Base.metadata.drop_all(bind=engine)

    @patch("data_sources.wifiinfo.copy_to_model.WifiInfoImporter.get_os_meta_list")
    @patch("data_sources.wifiinfo.copy_to_model.WifiInfoImporter.get_os_file_stream")
    def test_copy_wifiinfo(self, file_stream, meta_list, c_parse):
        csvfile = open(FIXTURE_PATH + '/wifiinfo.csv', 'rb')

        meta_list.return_value = [{'name': 'wifiinfo.csv'}]
        c_parse.side_effect = [ArgumentParser()]
        file_stream.side_effect = [csvfile]
        copy_to_model.main(make_engine=False)

        csvfile_count = session.query(models.CSVFileInfo).count()
        clean_count = session.query(models.WifiInfo).count()
        self.assertEqual(csvfile_count, 1)
        self.assertEqual(clean_count, 47)
        self.assertEqual(session.query(models.WifiInfo).all()[0].csv_name, 'wifiinfo.csv')
