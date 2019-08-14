from unittest.mock import patch

from django.conf import settings
from django.core.management import call_command
from django.test import TestCase

from apps.base.models import District, Neighbourhood

EXAMPLES_PATH = settings.BASE_DIR + '/apps/base/tests'


@patch('apps.base.management.commands.import_areas.Command.get_wfs_as_geojson_text', autospec=True)
class TestImportWFS(TestCase):

    def test_ok(self, geojson):
        geojson.side_effect = [
            open(EXAMPLES_PATH + '/stadsdeel_example.json').read(),
            open(EXAMPLES_PATH + '/buurt_simple_example.json').read()
        ]
        call_command('import_areas')

        self.assertEqual(District.objects.count(), 1)
        self.assertEqual(Neighbourhood.objects.count(), 1)

        district = District.objects.first()
        self.assertEqual(district.id, '03630000000020')
        self.assertEqual(district.code, 'B')
        self.assertEqual(district.wkb_geometry.srid, 4326)

        neighbourhood = Neighbourhood.objects.first()
        self.assertEqual(neighbourhood.id, '03630000000485')
        self.assertEqual(neighbourhood.code, '92a')
        self.assertEqual(neighbourhood.wkb_geometry.srid, 4326)
