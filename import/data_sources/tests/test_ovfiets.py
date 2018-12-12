import json
import logging
import unittest
from unittest.mock import patch

import db_helper
from data_sources.ovfiets import copy_to_model, models, slurp
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
    def __init__(self, *args, **kwargs):
        pass

    def parse_args(self):
        return self

    def add_argument(self, *args, **kwargs):
        pass


class TestDBWriting(unittest.TestCase):
    """Test writing to database."""
    fixture_path = FIX_DIR + "/data_sources/ovfiets/fixtures"

    @patch("data_sources.ovfiets.slurp.argparse")
    @patch("data_sources.ovfiets.copy_to_model.argparse")
    @patch("data_sources.ovfiets.slurp.fetch_json")
    def test_slurp_and_import_ovfiets(self, fetch_json_mock, c_parse, s_parse):
        with open(self.fixture_path + '/ovfiets.json') as json_file:
            json_data = json.loads(json_file.read())

        fetch_json_mock.side_effect = [json_data]
        slurp.main(make_engine=False)

        raw_count = session.query(models.OvFietsRaw).count()
        self.assertEqual(raw_count, 1)

        input_parser = ArgumentParser()
        input_parser.link_areas = False
        c_parse.ArgumentParser.side_effect = [input_parser]
        copy_to_model.main(make_engine=False)

        count = session.query(models.OvFiets).count()
        self.assertEqual(count, 2)

        sql = """
        UPDATE importer_ovfiets
        SET stadsdeel = 'A'
        WHERE station_code = 'AA'
        """

        copy_to_model.link_areas(sql)

        count = session.query(models.OvFiets).filter_by(stadsdeel='A').count()
        self.assertEqual(count, 1)

        count = session.query(models.OvFiets).filter_by(stadsdeel=None).count()
        self.assertEqual(count, 1)

    @patch("data_sources.ovfiets.slurp.argparse")
    @patch("data_sources.ovfiets.slurp.start_import")
    def test_slurp_main(self, start_import, argparse):
        input_parser = ArgumentParser()
        input_parser.debug = True
        argparse.ArgumentParser.side_effect = [input_parser]
        slurp.main(make_engine=False)
        self.assertTrue(start_import.called)

    @patch("data_sources.ovfiets.copy_to_model.argparse")
    @patch("data_sources.ovfiets.copy_to_model.start_import")
    def test_copy_to_model_main(self, start_import, argparse):
        input_parser = ArgumentParser()
        input_parser.link_areas = False
        argparse.ArgumentParser.side_effect = [input_parser]
        copy_to_model.main(make_engine=False)
        self.assertTrue(start_import.called)
