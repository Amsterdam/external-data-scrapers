import json
import logging
import unittest
from unittest.mock import patch

import db_helper
from data_sources.parkeergarages import copy_to_model, models, slurp
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
    link_areas = False

    def __init__(self, *args, **kwargs):
        pass

    def parse_args(self):
        return self

    def add_argument(self, *args, **kwargs):
        pass


class TestParkeerGarages(unittest.TestCase):
    """Test writing to database."""
    fixture_path = FIX_DIR + "/data_sources/fixtures"

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

    @patch("data_sources.parkeergarages.copy_to_model.argparse")
    @patch("data_sources.parkeergarages.slurp.argparse")
    @patch("data_sources.parkeergarages.slurp.fetch_json")
    def test_copy_parking_location(self, fetch_json_mock, s_parse, c_parse):
        with open(self.fixture_path + '/parking_location.json') as json_file:
            json_data = json.loads(json_file.read())

        fetch_json_mock.side_effect = [json_data]
        input_parser = ArgumentParser()
        input_parser.endpoint = ['parking_location']
        s_parse.ArgumentParser.side_effect = [input_parser]
        slurp.main(make_engine=False)

        c_parse.ArgumentParser.side_effect = [input_parser]

        copy_to_model.main(make_engine=False)

        model = models.ParkingLocation
        raw_count = session.query(model).count()
        self.assertEqual(raw_count, 3)

        obj = session.query(model).filter(model.api_id == '1').first()

        self.assertEqual(obj.name, 'CE-P28 PTA Touringcars')
        self.assertEqual(obj.free_space_short, 345)
        self.assertEqual(obj.free_space_long, 446)
        self.assertEqual(obj.short_capacity, 500)
        self.assertEqual(obj.long_capacity, 500)
        self.assertEqual(
            obj.pub_date.isoformat(), '2018-12-18T10:12:41.925000'
        )

    @patch("data_sources.parkeergarages.copy_to_model.settings")
    @patch("data_sources.parkeergarages.copy_to_model.argparse")
    @patch("data_sources.parkeergarages.slurp.argparse")
    @patch("data_sources.parkeergarages.slurp.fetch_json")
    def test_copy_parking_location_batch(self, fetch_json_mock,
                                         s_parse, c_parse, settings
                                         ):
        with open(self.fixture_path + '/parking_location.json') as json_file:
            json_data = json.loads(json_file.read())

        fetch_json_mock.side_effect = [json_data]
        input_parser = ArgumentParser()
        input_parser.endpoint = ['parking_location']
        s_parse.ArgumentParser.side_effect = [input_parser]
        slurp.main(make_engine=False)

        c_parse.ArgumentParser.side_effect = [input_parser]

        copy_to_model.main(make_engine=False)

        model = models.ParkingLocation
        raw_count = session.query(model).count()
        self.assertEqual(raw_count, 3)

        settings.DATABASE_IMPORT_LIMIT = 2

        # slurp 5 raw entries
        for _ in range(5):
            fetch_json_mock.side_effect = [json_data]
            s_parse.ArgumentParser.side_effect = [input_parser]
            slurp.main(make_engine=False)

        c_parse.ArgumentParser.side_effect = [input_parser]
        copy_to_model.main(make_engine=False)
        raw_count = session.query(model).count()
        self.assertEqual(raw_count, 18)

    @patch("data_sources.parkeergarages.copy_to_model.argparse")
    @patch("data_sources.parkeergarages.slurp.argparse")
    @patch("data_sources.parkeergarages.slurp.fetch_json")
    def test_copy_guidance_sign(self, fetch_json_mock, s_parse, c_parse):
        with open(self.fixture_path + '/guidance_sign.json') as json_file:
            json_data = json.loads(json_file.read())

        fetch_json_mock.side_effect = [json_data]
        input_parser = ArgumentParser()
        input_parser.endpoint = ['guidance_sign']
        s_parse.ArgumentParser.side_effect = [input_parser]
        slurp.main(make_engine=False)

        c_parse.ArgumentParser.side_effect = [input_parser]

        copy_to_model.main(make_engine=False)

        model = models.GuidanceSign
        raw_count = session.query(model).count()
        self.assertEqual(raw_count, 4)

        obj = session.query(model).filter(model.api_id == '1').first()

        self.assertEqual(obj.state, "ok")
        self.assertEqual(
            obj.name, 'FJ462B13 - ZO-B13 Burg.Stramanweg 02510/080'
        )
        self.assertEqual(
            obj.pub_date.isoformat(), '2018-12-18T09:56:41.930000'
        )

        model = models.ParkingGuidanceDisplay
        raw_count = session.query(model).count()
        self.assertEqual(raw_count, 4)

        obj = session.query(model).filter(model.api_id == '4').first()

        self.assertEqual(obj.output_description, 'GEDOOFD')
        self.assertEqual(obj.type, "VVX")
        self.assertEqual(obj.output, "GEDOOFD")
        self.assertEqual(obj.guidance_sign_id, '3')
        self.assertEqual(
            obj.description, 'CE74_VVX_ Stadhouderskade 03277/005_P Byzantium'
        )
        self.assertEqual(
            obj.pub_date.isoformat(), '2018-12-18T09:56:41.930000'
        )

    @patch("data_sources.parkeergarages.copy_to_model.settings")
    @patch("data_sources.parkeergarages.copy_to_model.argparse")
    @patch("data_sources.parkeergarages.slurp.argparse")
    @patch("data_sources.parkeergarages.slurp.fetch_json")
    def test_copy_guidance_sign_batch(
            self, fetch_json_mock, s_parse, c_parse, settings
    ):
        with open(self.fixture_path + '/guidance_sign.json') as json_file:
            json_data = json.loads(json_file.read())

        fetch_json_mock.side_effect = [json_data]
        input_parser = ArgumentParser()
        input_parser.endpoint = ['guidance_sign']
        s_parse.ArgumentParser.side_effect = [input_parser]
        slurp.main(make_engine=False)

        c_parse.ArgumentParser.side_effect = [input_parser]

        copy_to_model.main(make_engine=False)

        model = models.GuidanceSign
        raw_count = session.query(model).count()
        obj = session.query(model).filter(model.api_id == '1').first()

        self.assertEqual(raw_count, 4)
        self.assertEqual(
            obj.name, 'FJ462B13 - ZO-B13 Burg.Stramanweg 02510/080'
        )

        settings.DATABASE_IMPORT_LIMIT = 2

        # slurp 5 raw entries
        json_data['features'][0]['properties']['Name'] = 'Updated'

        for _ in range(5):
            fetch_json_mock.side_effect = [json_data]
            s_parse.ArgumentParser.side_effect = [input_parser]
            slurp.main(make_engine=False)

        c_parse.ArgumentParser.side_effect = [input_parser]
        copy_to_model.main(make_engine=False)
        raw_count = session.query(model).count()

        obj = session.query(model).filter(model.api_id == '1').first()

        # No new guidance signs were added because they are updated
        self.assertEqual(raw_count, 4)
        self.assertEqual(obj.name, 'Updated')
