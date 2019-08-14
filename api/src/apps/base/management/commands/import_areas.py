import logging

import requests
from django.contrib.gis.utils import LayerMapping
from django.core.management.base import BaseCommand

from apps.base.models import District, Neighbourhood

log = logging.getLogger(__name__)

DISTRICT_URL = "https://map.data.amsterdam.nl/maps/gebieden?REQUEST=GetFeature&srsName=EPSG:4326&TYPENAME=stadsdeel&SERVICE=WFS&VERSION=2.0.0&outputformat=geojson" # noqa

NEIGHBOURHOOD_URL = "https://map.data.amsterdam.nl/maps/gebieden?REQUEST=GetFeature&srsName=EPSG:4326&TYPENAME=buurt_simple&SERVICE=WFS&VERSION=2.0.0&outputformat=geojson" # noqa


class Command(BaseCommand):
    help = "import the gebieden wfs into the db"

    def handle(self, *args, **options):
        for model, url in [(District, DISTRICT_URL), (Neighbourhood, NEIGHBOURHOOD_URL)]:
            self.import_model(model, url)

    def import_model(self, model, url):
        self.empty_model(model)

        log.info(f"Truncated {model}")

        layer_mapping = LayerMapping(
            model,
            self.get_wfs_as_geojson_text(url),
            self.generate_model_mapping(model)
        )
        log.info(f"Saving layer to db")
        layer_mapping.save()

    def empty_model(self, model):
        '''Clean the model empty before repopulating it'''
        model.objects.all().delete()

    def get_wfs_as_geojson_text(self, url):
        '''
        Retrieve the geojson as text because the `LayerMapping`
        uril expects text
        '''
        return requests.get(url).text

    def generate_model_mapping(self, model):
        '''Generate mapping from field names since the names are identical to the file'''
        mapping = {field.name: field.name for field in model._meta.get_fields()}
        mapping['wkb_geometry'] = 'POLYGON'
        return mapping
