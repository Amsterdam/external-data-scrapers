from apps.base.base_importer import BaseImportFactory


class GeoJsonImportFactory(BaseImportFactory):
    '''
    BaseimportFactory extension for GeoJSON format.
    Extracts the nested `properties` json from the
    raw_data.
    '''
    def extract_properties(self, raw_data):
        properties = raw_data.pop('properties')
        raw_data.update(properties)
        return raw_data

    def prepare_raw_data(self, raw_data):
        raw_data = self.extract_properties(raw_data)
        return super().prepare_raw_data(raw_data)
