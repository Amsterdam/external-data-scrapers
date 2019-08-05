import logging

from django.contrib.gis.geos import Point
from django.core.management.base import BaseCommand
from django.db.models import FieldDoesNotExist

from apps.boat_tracking.models import BoatTracking, BoatTrackingRaw

logging.basicConfig(level=logging.DEBUG, format='%(message)s')
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


class Command(BaseCommand):
    def handle(self, *args, **options):
        log.info("Starting import")
        ImportBoatTracking().start()
        log.info("import Done")


class ImportBoatTracking:
    '''
    Class used to unpack BoatTrackingRaw records, clean them then
    insert them into BoatTracking model
    and save it in the processed table.
    '''
    mapped_keys = {'Id': 'mmsi', 'Position': 'geo_location'}

    def set_key_if_exists(self, model_instance, key, value):
        '''
        Checks if key exists in model then sets the attribute to the instance.
        '''
        try:
            if key in self.mapped_keys:
                key = self.mapped_keys[key]
            field = model_instance._meta.get_field(key.lower())
            setattr(model_instance, field.name, value)
        except FieldDoesNotExist:
            pass

    def augment(self, key, value):
        '''
        Augment the key value pair with specific information.
        Currently only creates a geo object.
        '''
        if key == 'Position':
            value = Point(value['x'], value['y'], srid=4326)
        return key, value

    def map_to_clean_model(self, batch):
        '''
        Loop through the rows in each batch record and
        map the keys to the model fields.
        The `mapped_keys` dict defines the keys that require changing.
        The keys will be cross checked with the model fields after applying
        `.lower()` to them.

        Process:
            - Create the clean_batch list for bulk insert
            - Loop through the rows in the batch
            - Loop through the json list in the data field
            - Loop through the key value pain in each record
            - Call the `augment()` method to augment the pair
            - Check if the key exists in the model then save it
            - Add the model instance to the clean_batch list
            - Repeat from step 2
        '''
        clean_batch = []

        for row in batch:
            for data_instance in row.data:
                model_instance = BoatTracking()

                for key, value in data_instance.items():
                    key, value = self.augment(key, value)
                    self.set_key_if_exists(model_instance, key, value)
                model_instance.scraped_at = row.scraped_at
                clean_batch.append(model_instance)
        return clean_batch

    def store(self, clean_batch):
        '''Bulk insert the cleaned batch'''
        BoatTracking.objects.bulk_create(clean_batch, len(clean_batch))

    def start(self):
        '''
        Process:
            - Retrieve the query iterator from the manager
            - Clean the batch
            - Store it
        '''

        query_iterator = BoatTrackingRaw.objects.query_iterator(10)
        for batch in query_iterator:
            clean_batch = self.map_to_clean_model(batch)
            self.store(clean_batch)
