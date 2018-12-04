import json
import logging
import unittest
from unittest.mock import patch

import db_helper
from data_sources.ovfiets import cleanup, models, slurp
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


class TestDBWriting(unittest.TestCase):
    """Test writing to database."""
    fixture_path = FIX_DIR + "/data_sources/ovfiets/fixtures"

    @patch("data_sources.ovfiets.slurp.fetch_json")
    def test_slurp_and_import_ovfiets(self, fetch_json_mock):

        with open(self.fixture_path + '/ovfiets.json') as json_file:
            json_data = json.loads(json_file.read())

        fetch_json_mock.side_effect = [json_data]
        slurp.start_import(make_engine=False)

        raw_count = session.query(models.OvFietsRaw).count()
        self.assertEqual(raw_count, 1)

        cleanup.start_import()

        count = session.query(models.OvFiets).count()
        self.assertEqual(count, 2)
