import logging
import unittest
from datetime import datetime, timedelta
from unittest.mock import patch

import db_helper
from data_sources.trafficorder import copy_to_model, models, slurp
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
    year = 2019
    monthly = True
    link_areas = False

    def __init__(self, **kwargs):
        for name in kwargs:
            setattr(self, name, kwargs[name])


@patch("data_sources.trafficorder.slurp.argparse.ArgumentParser.parse_args")
@patch("data_sources.trafficorder.slurp.TrafficOrderSlurper.fetch")
class TestSlurpTrafficOrder(unittest.TestCase):
    """Test writing to database."""

    def setUp(self):
        global engine
        models.Base.metadata.create_all(bind=engine)

    def tearDown(self):
        global engine
        session.close()
        models.Base.metadata.drop_all(bind=engine)

    def test_slurp_trafficorder(self, fetch, s_parse):
        with open(
                FIXTURE_PATH + '/trafficorder.xml', 'rb'
        ) as gz_xml_file:
            xml_data = gz_xml_file.read()

        inputparser = ArgumentParser()
        s_parse.side_effect = [inputparser]

        fetch.side_effect = [xml_data]
        slurp.main(make_engine=False)

        raw_count = session.query(models.TrafficOrderRaw).count()
        self.assertEqual(raw_count, 1)

    def test_slurp_trafficorder_month(self, fetch, s_parse):
        with open(
                FIXTURE_PATH + '/trafficorder.xml', 'rb'
        ) as gz_xml_file:
            xml_data = gz_xml_file.read()

        inputparser = ArgumentParser(month=12)
        s_parse.side_effect = [inputparser]

        fetch.side_effect = [xml_data]
        slurp.main(make_engine=False)

        raw_count = session.query(models.TrafficOrderRaw).count()
        self.assertEqual(raw_count, 1)

    def test_url_query_trafficorder(self, fetch, s_parse):
        slurper = slurp.TrafficOrderSlurper(monthly=True)
        m = datetime.today().replace(day=1) - timedelta(days=1)
        self.assertEqual(
            slurper.date_query,
            f'and(jaargang={m.year})and(date>{m.year}-{m.month}-1)and(date<{m.year}-{m.month}-{m.day})'
        )

        slurper = slurp.TrafficOrderSlurper(year=1992)
        self.assertEqual(slurper.date_query, 'and(jaargang=1992)')


@patch("data_sources.trafficorder.copy_to_model.argparse.ArgumentParser.parse_args")
@patch("data_sources.trafficorder.copy_to_model.TrafficOrderImporter.fetch")
class TestCopyTrafficOrder(unittest.TestCase):
    """Test writing to database."""

    def setUp(self):
        global engine
        models.Base.metadata.create_all(bind=engine)

    def tearDown(self):
        global engine
        session.close()
        models.Base.metadata.drop_all(bind=engine)

    def _populate_raw_trafficorder(self):
        with open(FIXTURE_PATH + '/trafficorder.xml', 'rb') as xml:
            session.add(models.TrafficOrderRaw(
                id=1, scraped_at=datetime.now(), data=xml.read(), year=2019
            ))
            session.commit()

    def test_copy_trafficorder(self, fetch, c_parse):
        self._populate_raw_trafficorder()
        with open(
                FIXTURE_PATH + '/trafficorder_meta.xml', 'rb'
        ) as gz_xml_file:
            xml_data = gz_xml_file.read()

        inputparser = ArgumentParser()
        c_parse.side_effect = [inputparser]

        fetch.side_effect = [xml_data]
        copy_to_model.main(make_engine=False)

        raw_count = session.query(models.TrafficOrder).count()
        self.assertEqual(raw_count, 1)

    def test_copy_multiple_signs_and_geo_trafficorder(self, fetch, c_parse):
        self._populate_raw_trafficorder()
        with open(
                FIXTURE_PATH + '/trafficorder_meta_multiple.xml', 'rb'
        ) as gz_xml_file:
            xml_data = gz_xml_file.read()

        inputparser = ArgumentParser()
        c_parse.side_effect = [inputparser]

        fetch.side_effect = [xml_data]
        copy_to_model.main(make_engine=False)

        raw_count = session.query(models.TrafficOrder).count()
        self.assertEqual(raw_count, 3)
