import logging
import unittest
from unittest.mock import patch

import db_helper
from data_sources.ndw import copy_to_model, models, slurp
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

    def __init__(self, **kwargs):
        for name in kwargs:
            setattr(self, name, kwargs[name])


@patch("data_sources.ndw.slurp.argparse.ArgumentParser.parse_args")
@patch("data_sources.ndw.slurp.NDWSlurper.fetch")
class TestDBWriting(unittest.TestCase):
    """Test writing to database."""
    fixture_path = FIX_DIR + "/data_sources/fixtures"

    def setUp(self):
        global engine
        models.Base.metadata.create_all(bind=engine)

    def tearDown(self):
        global engine
        session.close()
        models.Base.metadata.drop_all(bind=engine)

    def test_slurp_traveltime(self, fetch, s_parse):
        with open(
                self.fixture_path + '/traveltime.xml.gz', 'rb'
        ) as gz_xml_file:
            xml_data = gz_xml_file.read()

        inputparser = ArgumentParser(ndw=True)
        s_parse.side_effect = [inputparser]

        fetch.side_effect = [xml_data]
        slurp.main(make_engine=False)

        raw_count = session.query(models.TravelTimeRaw).count()
        self.assertEqual(raw_count, 1)

    def test_copy_traveltime(self, fetch, s_parse):
        with open(
                self.fixture_path + '/traveltime.xml.gz', 'rb'
        ) as gz_xml_file:
            xml_data = gz_xml_file.read()

        inputparser = ArgumentParser(ndw=True)
        s_parse.side_effect = [inputparser]
        fetch.side_effect = [xml_data]
        slurp.main(make_engine=False)

        copy_to_model.start_import(
            copy_to_model.store_ndw,
            models.TravelTimeRaw,
            "importer_traveltime"
        )
        raw_count = session.query(models.TravelTime).count()
        self.assertEqual(raw_count, 1)
