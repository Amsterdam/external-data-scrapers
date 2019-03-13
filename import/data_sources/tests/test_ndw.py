import logging
import unittest
from datetime import datetime
from unittest.mock import patch

import db_helper
from data_sources.ndw import copy_to_model, models, slurp
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
    endpoint = ['traveltime']

    def __init__(self, **kwargs):
        for name in kwargs:
            setattr(self, name, kwargs[name])


@patch("data_sources.ndw.slurp.argparse.ArgumentParser.parse_args")
class TestSlurpNDW(unittest.TestCase):
    """Test writing to database."""

    def setUp(self):
        global engine
        models.Base.metadata.create_all(bind=engine)

    def tearDown(self):
        global engine
        session.close()
        models.Base.metadata.drop_all(bind=engine)

    @patch("data_sources.ndw.slurp.TravelTimeSlurper.fetch")
    def test_slurp_traveltime(self, fetch, s_parse):
        with open(
                FIXTURE_PATH + '/traveltime.xml.gz', 'rb'
        ) as gz_xml_file:
            xml_data = gz_xml_file.read()

        inputparser = ArgumentParser()
        s_parse.side_effect = [inputparser]

        fetch.side_effect = [xml_data]
        slurp.main(make_engine=False)

        raw_count = session.query(models.TravelTimeRaw).count()
        self.assertEqual(raw_count, 1)

    @patch("data_sources.ndw.slurp.TrafficSpeedSlurper.fetch")
    def test_slurp_trafficspeed(self, fetch, s_parse):
        with open(
                FIXTURE_PATH + '/trafficspeed.xml.gz', 'rb'
        ) as gz_xml_file:
            xml_data = gz_xml_file.read()

        inputparser = ArgumentParser(endpoint=['trafficspeed'])
        s_parse.side_effect = [inputparser]

        fetch.side_effect = [xml_data]
        slurp.main(make_engine=False)

        raw_count = session.query(models.TrafficSpeedRaw).count()
        self.assertEqual(raw_count, 1)


@patch("data_sources.ndw.copy_to_model.argparse.ArgumentParser.parse_args")
class TestCopyNDW(unittest.TestCase):
    """Test writing to database."""

    def setUp(self):
        global engine
        models.Base.metadata.create_all(bind=engine)

    def tearDown(self):
        global engine
        session.close()
        models.Base.metadata.drop_all(bind=engine)

    def _populate_raw_traveltime(self):
        with open(FIXTURE_PATH + '/traveltime.xml.gz', 'rb') as gz:
            session.add(models.TravelTimeRaw(id=1, scraped_at=datetime.now(), data=gz.read()))
            session.commit()

    def _populate_raw_trafficspeed(self):
        with open(FIXTURE_PATH + '/trafficspeed.xml.gz', 'rb') as gz:
            session.add(models.TrafficSpeedRaw(id=1, scraped_at=datetime.now(), data=gz.read()))
            session.commit()

    def test_copy_traveltime(self, s_parse):
        self._populate_raw_traveltime()

        inputparser = ArgumentParser(exclude_areas=True)
        s_parse.side_effect = [inputparser]
        copy_to_model.main(make_engine=False)

        raw_count = session.query(models.TravelTime).count()
        self.assertEqual(raw_count, 1)

    @patch("data_sources.ndw.copy_to_model.TrafficSpeedImporter.get_stadsdeel_list", autospec=True)
    @patch("data_sources.ndw.copy_to_model.TrafficSpeedImporter.get_buurt_code_list", autospec=True)
    @patch("data_sources.ndw.copy_to_model.requests.get")
    def test_add_trafficspeed_coordinates(self, get, b_list, s_list, s_parse):
        self._populate_raw_trafficspeed()
        with open(
                FIXTURE_PATH + '/ndw_shapefile.zip', 'rb'
        ) as shapefile:
            shapefile_data = shapefile.read()

        class Response:
            content = shapefile_data

        get.side_effect = [Response()]
        inputparser = ArgumentParser(endpoint=['trafficspeed'], exclude_areas=False)
        s_parse.side_effect = [inputparser]

        copy_to_model.main(make_engine=False)
        trafficspeed = models.TrafficSpeed
        self.assertEqual(
            session.query(trafficspeed).filter(trafficspeed.geometrie is not None).count(), 1
        )

    @patch("data_sources.ndw.copy_to_model.TravelTimeImporter.get_stadsdeel_list", autospec=True)
    @patch("data_sources.ndw.copy_to_model.TravelTimeImporter.get_buurt_code_list", autospec=True)
    @patch("data_sources.ndw.copy_to_model.requests.get")
    def test_add_traveltime_coordinates(self, get, b_list, s_list, s_parse):
        self._populate_raw_traveltime()
        with open(
                FIXTURE_PATH + '/ndw_shapefile.zip', 'rb'
        ) as shapefile:
            shapefile_data = shapefile.read()

        class Response:
            content = shapefile_data

        get.side_effect = [Response()]
        inputparser = ArgumentParser(exclude_areas=False)
        s_parse.side_effect = [inputparser]

        copy_to_model.main(make_engine=False)
        traveltime = models.TravelTime
        self.assertEqual(
            session.query(traveltime).filter(traveltime.geometrie is not None).count(), 1
        )
