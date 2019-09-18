import logging

from django.core.exceptions import ValidationError

log = logging.getLogger(__name__)


class BaseImportFactory:
    '''
    Recieves raw data and returns a model instance.
    The raw data is cleaned and applied to the model.

    Several methods in this class can be overridden for fine tuning.

    To apply something to the raw_data, override `prepare_raw_data`
    To apply something to the model instance before returning it, override  finalize_model_instance`


    Attributes:
    -----------
    model_form: Form Class
        The model form of the import model that will clean the raw data

    raw_to_model_mapping: dict
        Contains the keys in the raw data that need to be converted to the model field names

    snapshot: Model instance
        The snapshot instance. Added here to fetch the scraped_at from it.
    '''
    model_form = None
    raw_to_model_fields = None
    snapshot = None

    def __init__(self, snapshot):
        self.snapshot = snapshot

    def assert_attributes(self):
        log_message = "Implementation of the BaseImportFactory must set the '{}' attribute"

        assert self.model_form, log_message.format('model_form')
        assert self.raw_to_model_fields, log_message.format('raw_to_model_fields')
        assert self.snapeshot, log_message.format('snapshot')

    def convert_keys(self, raw_data):
        '''
        Returns new raw_data dict with the keys converted to match
        the model field names. Uses raw_to_model_fields dict to map the keys
        '''
        new_raw_data = {}

        for key, value in raw_data.items():
            key = self.raw_to_model_fields.get(key, key)
            new_raw_data[key] = value

        return new_raw_data

    def prepare_raw_data(self, raw_data):
        '''
        Any preparations or changes that need to be applied
        to the raw_data should be done here before running validations.
        '''
        return self.convert_keys(raw_data)

    def finalize_model_instance(self, model_instance):
        '''
        Any changes or extra fields that need to applied to the model instance
        are done here after validation.
        '''
        model_instance.scraped_at = self.snapshot.scraped_at

    def build_model_instance(self, raw_data):
        '''
        Validates raw_data and creates a model instance using
        the model_form.
        '''
        prepared_data = self.prepare_raw_data(raw_data)
        model_form = self.model_form(data=prepared_data)

        if not model_form.is_valid():
            raise ValidationError(model_form.errors)

        self.finalize_model_instance(model_form.instance)
        return model_form.instance


class BaseSnapshotImporter:
    '''
    Recieves a snapshot instance that is processed using the defined import_factory then stores
    the result in the db in the db.

    Attributes:
    ----------
    import_factory: BaseImportFactory instance
        The import factory that will process the snapshot data.

    import_model: Model instance
        The model that the processed data will be saved in

    snapshot: Model instance
        The snapshot instance.
    '''
    import_factory = None
    import_model = None
    snapshot = None

    def __init__(self, snapshot):
        self.snapshot = snapshot

    def assert_attributes(self):
        log_message = "Implementation of the BaseSnapshotImporter must set the '{}' attribute"

        assert self.import_model, log_message.format('import_model')
        assert self.import_factory, log_message.format('import_factory')
        assert self.snapeshot, log_message.format('snapshot')

    def store(self, model_instance_list):
        '''Bulk insert the model_instance_list'''
        log.info(f'''
        Bulk saving {len(model_instance_list)} {self.import_model.__name__}
        scraped at {self.snapshot.scraped_at}
        ''')

        self.import_model.objects.bulk_create(
            model_instance_list,
            len(model_instance_list),
        )

    def fetch_raw_data_from_snapshot(self):
        '''
        Override for finetuning
        '''
        return self.snapshot.data

    def start_import(self):
        '''
        Generates model_instance_list from the snapshot data
        then calls `store` method to save the list in the db
        '''
        model_instance_list = []

        for raw_data in self.fetch_raw_data_from_snapshot():
            model_instance = self.import_factory(snapshot=self.snapshot).build_model_instance(raw_data)
            model_instance_list.append(
                model_instance
            )

        self.store(model_instance_list)
