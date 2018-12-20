import unittest
from unittest.mock import MagicMock, call

from data_sources.link_areas import link_areas

stadsdeel_query = """
UPDATE test_table tt
SET stadsdeel = s.code
FROM (SELECT * from stadsdeel) as s
WHERE ST_DWithin(s.wkb_geometry, tt.geometrie, 0)
AND stadsdeel IS NULL
AND tt.geometrie IS NOT NULL
"""

buurt_query = """
UPDATE test_table tt
SET buurt_code = b.vollcode
FROM (SELECT * from buurt_simple) as b
WHERE ST_DWithin(b.wkb_geometry, tt.geometrie, 0)
AND buurt_code is null
AND tt.geometrie IS NOT NULL
"""


class TestLinkAreas(unittest.TestCase):

    def test_link_areas(self):
        mock = MagicMock()
        link_areas(mock, 'test_table')

        self.assertEqual(
            call(stadsdeel_query), mock.execute.call_args_list[0]
        )
        self.assertEqual(
            call(buurt_query), mock.execute.call_args_list[1]
        )
        self.assertTrue(mock.commit.called)
