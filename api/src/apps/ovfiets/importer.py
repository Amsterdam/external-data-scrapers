import logging

from django.contrib.gis.geos import Point
from django.db.models import FieldDoesNotExist
from django.utils import timezone

from apps.base.models import District, Neighbourhood
from apps.ovfiets.models import OvFiets, OvFietsRaw

log = logging.getLogger(__name__)


class OvFietsImporter:
    '''
    Class used to unpack OvFietsRaw records.

    OVFietsRaw has a jsonfield called `data` that is a list of json objects.
    This list is looped through, cleaned then mapped one by one to an instance of the model
    OvFiets.

    The process of unpacking and cleaning is done in batches. The size of the batch
    is determined by the queryset fed to `queryset_to_model_instance_list` method.
    This batch is then bulk inserted in the db.

    Attributes
    ----------
    raw_to_model_mapping: dict
        Contains raw_instance keys that need to be mapped to the model field
    '''
    raw_to_model_mapping = {
        'openingHours': 'opening_hours',
        'locationCode': 'location_code',
        'stationCode': 'station_code',
        'fetchTime': 'fetch_time',
        'rentalBikes': 'rental_bikes'
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

    def set_to_model_field(self, model_instance, key, value):
        '''
        Populates model instance with field if it exists.
        Specific to this datasource, we dump all non existing fields to
        the jsonfield `unmapped`

        Args:
            model_instance (:obj:ModelInstance): instance of OvFiets model
            key (str): raw instance key string
            value (any): raw instance value (can be different types)

        Raises:
            FieldDoesNotExist: If field was not found on the model.
        '''
        try:
            field = model_instance._meta.get_field(key)
            setattr(model_instance, field.name, value)
        except FieldDoesNotExist:
            log.debug(f"Field {key} does not exist. Adding to unmapped")
            model_instance.unmapped.update({key: value})

    def clean_value(self, key, value):
        '''
        Clean the value so it can be stored in the model.
        Currently only modifies the fetch_time key to make it timezone aware

        Args:
            key (str): raw instance key string
            value (any): raw instance value (can be different types)

        Return:
            tuple: returns the key and the modified or unchanged value
        '''
        if key == 'fetch_time':
            value = timezone.datetime.fromtimestamp(value, tz=timezone.utc)
        return key, value

    def extract_extra(self, data_instance):
        '''
        Extract the data in data_instance.extra (dict)
        and add each key-value combination to the data_instance object itself
        to be cleaned and added to the model instance.

        Args:
            data_instance (dict): one instance of the data list

        return
            data_instance (dict): modified instance of the data list
        '''
        extra = data_instance.pop('extra')
        data_instance.update(extra)
        return data_instance

    def extract_coordinates(self, data_instance):
        '''
        Extract the coordinates values and create
        a Point object

        Args:
            data_instance (dict): one instance of the data list

        return
            data_instance (dict): modified instance of the data list
        '''
        data_instance.update({
            'geometrie': Point(
                data_instance.pop('lng'),
                data_instance.pop('lat')
            )
        })
        return data_instance

    def build_model_instance(self, data_instance, timestamp):
        '''
        Build a model instance with the data instance items
        after cleaning the items.

        Args:
            data_instance (dict): one instance of the data list
            scraped_at (datetime): scraped timestamp of the instance

        Returns:
            OvFiets obj: populated model instance
        '''
        model_instance = OvFiets(scraped_at=timestamp, unmapped={})
        data_instance = self.extract_extra(data_instance)
        data_instance = self.extract_coordinates(data_instance)

        for key, value in data_instance.items():
            key = self.clean_key(key)
            key, value = self.clean_value(key, value)
            self.set_to_model_field(model_instance, key, value)

        model_instance.stadsdeel = District.objects.get_district(model_instance.geometrie)

        # If no district then it is not in Amsterdam. Skipping the neighbourhood saves computing time.
        if model_instance.stadsdeel:
            model_instance.buurt_code = Neighbourhood.objects.get_neighbourhood(model_instance.geometrie)

        return model_instance

    def store(self, model_instance_list):
        '''Bulk insert the model_instance_list'''
        log.info(f"Bulk saving {len(model_instance_list)} records")
        OvFiets.objects.bulk_create(model_instance_list, len(model_instance_list))

    def queryset_to_model_instance_list(self, queryset):
        '''
        Each raw_instance contains a jsonfield list of objects. This method
        loops through the objects to map them to model instances then returns
        a list of model instances that will then be bulk inserted.

        Args:
            queryset (django queryset): OvFietsRaw Queryset

        Returns:
            list: list of model_instances
        '''
        model_instance_list = []

        for raw_instance in queryset:
            log.info(f"Raw record scraped_at {raw_instance.scraped_at} raw records")
            #  raw_instance contains multiple data instances as a json list
            for data_instance in raw_instance.data['locaties'].values():
                model_instance_list.append(
                    self.build_model_instance(data_instance, raw_instance.scraped_at)
                )
        return model_instance_list

    def start(self):
        query_iterator = OvFietsRaw.objects.query_iterator(10)
        for queryset in query_iterator:
            log.info(f"Processing {len(queryset)} raw records")
            model_instance_list = self.queryset_to_model_instance_list(queryset)
            self.store(model_instance_list)
