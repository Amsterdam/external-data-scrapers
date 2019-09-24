from django.contrib.gis import forms, geos

from apps.constants import WGS84_SRID
from apps.parkeergarages import constants
from apps.parkeergarages.models import (GuidanceSign, ParkingGuidanceDisplay,
                                        ParkingLocation)


class GeoJsonPointField(forms.PointField):
    def to_python(self, value):
        return geos.Point(
            value['coordinates'][0],
            value['coordinates'][1],
            srid=WGS84_SRID
        )


class ParkingLocationImporterForm(forms.ModelForm):
    pub_date = forms.DateTimeField(input_formats=['%Y-%m-%dT%H:%M:%S.%fz'])
    geometrie = GeoJsonPointField()

    class Meta:
        model = ParkingLocation
        fields = list(constants.PARKINGLOCATION_RAW_TO_MODEL_FIELDS.values())


class GuidanceSignImporterForm(forms.ModelForm):
    pub_date = forms.DateTimeField(input_formats=['%Y-%m-%dT%H:%M:%S.%f%z'])
    geometrie = GeoJsonPointField()

    def clean(self):
        '''
        The clean method normally validates unique fields here. This is overriden to
        avoid the unique validation since GuidanceSigns are updated on every import not appended to
        the table. Therefore, duplicate keys are expected.
        '''
        return self.cleaned_data

    class Meta:
        model = GuidanceSign
        fields = list(constants.GUIDANCESIGN_RAW_TO_MODEL_FIELDS.values())


class ParkingGuidanceDisplayImporterForm(forms.ModelForm):
    class Meta:
        model = ParkingGuidanceDisplay
        fields = list(constants.PARKINGGUIDANCEDISPLAY_RAW_TO_MODEL_FIELDS.values())
