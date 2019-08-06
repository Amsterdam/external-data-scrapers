import logging

from django.contrib.gis.geos import Point
from django.db.models import FieldDoesNotExist

from apps.boat_tracking.models import BoatTracking, BoatTrackingRaw

logging.basicConfig(level=logging.DEBUG, format='%(message)s')
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


class ImportBoatTracking:
    '''
    Class used to unpack BoatTrackingRaw records, clean them then
    insert them into BoatTracking model

    altered_keys is a dictionary containing the keys in the raw instances
    that need to be altered to the model field

    For example, the scraped api calls the geo field "Position" while
    in the model it is called "geo_location"
    '''
    altered_keys = {'Id': 'mmsi',
                    'Position': 'geo_location',
                    'Name': 'name',
                    'Type': 'type',
                    'Length': 'length',
                    'Width': 'width',
                    'Speed': 'speed',
                    'Direction': 'direction',
                    'Status': 'status',
                    'Sensor': 'sensor',
                    'Lastupdate': 'lastupdate',
                    'LastMoved': 'lastmoved'
                    }

    def clean_key(self, key):
        '''
        Checks if key needs to be altered
        '''
        if key in self.altered_keys:
            key = self.altered_keys[key]
        return key

    def clean_value(self, key, value):
        '''
        Parses the geo_location value into a Point object.
        '''
        if key == 'geo_location':
            value = Point(value['x'], value['y'], srid=4326)
        return key, value

    def set_to_model_field(self, model_instance, key, value):
        '''
        Checks if field exists then saves it to the model instance
        '''
        try:
            field = model_instance._meta.get_field(key)
            setattr(model_instance, field.name, value)
        except FieldDoesNotExist as e:
            log.error(e)

    def build_model_instance(self, data_instance, timestamp):
        '''
        Build a model instance with the data instance items
        after cleaning the items.
        '''
        model_instance = BoatTracking()

        for key, value in data_instance.items():
            key = self.clean_key(key)
            key, value = self.clean_value(key, value)
            self.set_to_model_field(model_instance, key, value)

        model_instance.scraped_at = timestamp
        return model_instance

    def queryset_to_model_instance_list(self, queryset):
        '''
        Creates a model instance list from the queryset.

        Process:
            - Create empty model_instance list
            - Loop through the raw_instances in the queryset
            - Loop through the data_instances in the raw_instance json field
            - Build a model_instance
            - Append to lis
            - Repeat from step 2
        '''
        model_instance_list = []

        for raw_instance in queryset:
            #  raw_instance contains multiple data instances as a json list
            for data_instance in raw_instance.data:
                model_instance_list.append(
                    self.build_model_instance(data_instance, raw_instance.scraped_at)
                )
        return model_instance_list

    def store(self, clean_batch):
        '''Bulk insert the cleaned batch'''
        BoatTracking.objects.bulk_create(clean_batch, len(clean_batch))

    def start(self):
        '''
        Process:
            - Retrieve the query iterator from the manager
            - Map to model instances
            - Store the model instances list
        '''
        query_iterator = BoatTrackingRaw.objects.query_iterator(10)
        for queryset in query_iterator:
            model_instance_list = self.queryset_to_model_instance_list(queryset)
            self.store(model_instance_list)
