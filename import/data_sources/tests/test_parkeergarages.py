import json
import logging
import unittest
from unittest.mock import patch

import db_helper
from data_sources.parkeergarages import models, slurp
from settings import BASE_DIR, TESTING

log = logging.getLogger(__name__)

FIX_DIR = BASE_DIR

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

    def __init__(self, *args, **kwargs):
        pass

    def parse_args(self):
        return self

    def add_argument(self, *args, **kwargs):
        pass


class TestParkeerGarages(unittest.TestCase):
    """Test writing to database."""
    fixture_path = FIX_DIR + "/data_sources/ovfiets/fixtures"

    def setUp(self):
        global engine
        models.Base.metadata.create_all(bind=engine)

    def tearDown(self):
        global engine
        session.close()
        models.Base.metadata.drop_all(bind=engine)

    @patch("data_sources.parkeergarages.slurp.argparse")
    @patch("data_sources.parkeergarages.slurp.fetch_json")
    def test_slurp_guidance_sign(self, fetch_json_mock, s_parse):
        with open(self.fixture_path + '/guidance_sign.json') as json_file:
            json_data = json.loads(json_file.read())

        fetch_json_mock.side_effect = [json_data]

        input_parser = ArgumentParser()
        input_parser.endpoint = ['guidance_sign']
        s_parse.ArgumentParser.side_effect = [input_parser]
        slurp.main(make_engine=False)

        raw_count = session.query(models.GuidanceSignRaw).count()
        self.assertEqual(raw_count, 1)

    @patch("data_sources.parkeergarages.slurp.argparse")
    @patch("data_sources.parkeergarages.slurp.fetch_json")
    def test_slurp_parking_location(self, fetch_json_mock, s_parse):
        with open(self.fixture_path + '/parking_location.json') as json_file:
            json_data = json.loads(json_file.read())

        fetch_json_mock.side_effect = [json_data]

        input_parser = ArgumentParser()
        input_parser.endpoint = ['parking_location']
        s_parse.ArgumentParser.side_effect = [input_parser]
        slurp.main(make_engine=False)

        raw_count = session.query(models.ParkingLocationRaw).count()
        self.assertEqual(raw_count, 1)
