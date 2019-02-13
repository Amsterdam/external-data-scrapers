import logging
import unittest
from unittest.mock import patch

import db_helper

log = logging.getLogger(__name__)


class TestDBHelper(unittest.TestCase):
    """Test writing to database."""

    def test_environment_override(self):
        environ = {
            'DATABASE_OVERRIDE_HOST': 'host',
            'DATABASE_OVERRIDE_PORT': '20',
            'DATABASE_OVERRIDE_NAME': 'db_name',
            'DATABASE_OVERRIDE_USER': 'username',
            'DATABASE_OVERRIDE_PASSWORD': 'password',
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
            'postgresql://username:password@host:20/db_name'
        )
