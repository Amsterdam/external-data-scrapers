import logging
import unittest
from unittest.mock import patch

import db_helper

log = logging.getLogger(__name__)


class TestDBHelper(unittest.TestCase):
    """Test writing to database."""

    def test_environment_override(self):
        environ = {
            'DATABASE_OVERRIDE_HOST': 'test',
            'DATABASE_OVERRIDE_PORT': '20',
            'DATABASE_OVERRIDE_NAME': 'test',
            'DATABASE_OVERRIDE_USER': 'test',
            'DATABASE_OVERRIDE_PASSWORD': 'test',
        }

        with patch.dict('db_helper.os.environ', environ):
            conf = db_helper.make_conf('docker')

        self.assertEqual(
            str(conf),
            'postgresql://externaldata:insecure@database:5432/externaldata'
        )

        environ['OVERRIDE_DATABASE'] = 'true'

        with patch.dict('db_helper.os.environ', environ):
            conf = db_helper.make_conf('docker')

        self.assertEqual(
            str(conf),
            'postgresql://test:test@test:20/test'
        )
