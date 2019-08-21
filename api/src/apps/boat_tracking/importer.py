import logging

from django.contrib.gis.geos import Point
from django.db.models import FieldDoesNotExist

from apps.boat_tracking.models import BoatTracking, BoatTrackingRaw

log = logging.getLogger(__name__)


class BoatTrackingImporter:
    '''
    Class used to unpack BoatTrackingRaw records.

    BoatTrackingRaw has a jsonfield called `data` that is a list of json objects.
    This list is looped through, cleaned then mapped one by one to an instance of the model
    BoatTracking.

    The process of unpacking and cleaning is done in batches. The size of the batch
    is determined by the queryset fed to `queryset_to_model_instance_list` method.
    This batch is then bulk inserted in the db.

    Attributes
    ----------
    raw_to_model_mapping: dict
        Contains raw_instance keys that need to be mapped to the model field
    '''
    raw_to_model_mapping = {
        'Id': 'mmsi',
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
        Checks if the raw key needs to be mapped to a model
        attribute with a different name

        Args:
            key (str): raw instance key string

        Returns:
            str: the mapped or unchanged key
        '''
        if key in self.raw_to_model_mapping:
            key = self.raw_to_model_mapping[key]
        return key

    def clean_value(self, key, value):
        '''
        Clean the value so it can be stored in the model.
        Currently only modifies the geo_location value to a Point object

        Args:
            key (str): raw instance key string
            value (any): raw instance value (can be different types)

        Return:
            tuple: returns the key and the modified or unchanged value
        '''
        if key == 'geo_location':
            value = Point(value['x'], value['y'], srid=4326)
        return key, value

    def set_to_model_field(self, model_instance, key, value):
        '''
        Populates model instance with field if it exists.

        Args:
            model_instance (:obj:ModelInstance): instance of BoatTracking model
            key (str): raw instance key string
            value (any): raw instance value (can be different types)

        Raises:
            FieldDoesNotExist: If field was not found on the model.
        '''
        try:
            field = model_instance._meta.get_field(key)
            setattr(model_instance, field.name, value)
        except FieldDoesNotExist as e:
            log.error(e)

    def build_model_instance(self, data_instance, scraped_at):
        '''
        Build a model instance with the data instance items
        after cleaning the items.

        Args:
            data_instance (dict): one instance of the data list
            scraped_at (datetime): scraped timestamp of the instance

        Returns:
            BoatTracking obj: populated model instance
        '''
        model_instance = BoatTracking()

        for key, value in data_instance.items():
            key = self.clean_key(key)
            key, value = self.clean_value(key, value)
            self.set_to_model_field(model_instance, key, value)

        model_instance.scraped_at = scraped_at
        return model_instance

    def store(self, model_instance_list):
        '''Bulk insert the model_instance_list'''
        log.info(f"Bulk saving {len(model_instance_list)} records")
        BoatTracking.objects.bulk_create(model_instance_list, len(model_instance_list))

    def queryset_to_model_instance_list(self, queryset):
        '''
        Each raw_instance contains a jsonfield list of objects. This method
        loops through the objects to map them to model instances then returns
        a list of model instances that will then be bulk inserted.

        Args:
            queryset (django queryset): BoatTrackingRaw Queryset

        Returns:
            list: list of model_instances
        '''
        model_instance_list = []

        for raw_instance in queryset:
            log.info(f"Raw record scraped_at {raw_instance.scraped_at} raw records")
            #  raw_instance contains multiple data instances as a json list
            for data_instance in raw_instance.data:
                model_instance_list.append(
                    self.build_model_instance(data_instance, raw_instance.scraped_at)
                )
        return model_instance_list

    def start(self):
        query_iterator = BoatTrackingRaw.objects.query_iterator(10)
        for queryset in query_iterator:
            log.info(f"Processing {len(queryset)} raw records")
            model_instance_list = self.queryset_to_model_instance_list(queryset)
            self.store(model_instance_list)
