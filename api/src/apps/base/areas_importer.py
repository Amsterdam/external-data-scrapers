from apps.base.base_importer import BaseImportFactory
from apps.base.models import District, Neighbourhood


class AreasImportFactory(BaseImportFactory):
    '''
    BaseImportFactory extension that adds Amsterdam
    Areas to the model.

    Attributes:
    -----------
    areas_fields: dict
        Dict that contains the import model fieldnames of the areas.
        e.g the `neighbourhood_field` is named `buurt_code`.
    '''
    areas_fields = {
        'neighbourhood_field': 'buurt_code',
        'district_field': 'stadsdeel',
        'geometry_field': 'geometrie'
    }

    def finalize_model_instance(self, model_instance):
        super().finalize_model_instance(model_instance)
        self.add_areas(model_instance, **self.areas_fields)

    def add_areas(self, instance, neighbourhood_field, district_field, geometry_field):
        geo_location = getattr(instance, geometry_field)
        setattr(instance, district_field, District.objects.get_district(geo_location))

        # If no district then it is not in Amsterdam. Skipping the neighbourhood saves computing time.
        if getattr(instance, district_field):
            setattr(instance, neighbourhood_field, Neighbourhood.objects.get_neighbourhood(geo_location))
