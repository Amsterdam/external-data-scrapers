from django.contrib.gis import forms, geos

from apps.boat_tracking import constants
from apps.boat_tracking.models import BoatTracking


class CustomPointField(forms.PointField):
    def to_python(self, value):
        return geos.Point(
            value['x'],
            value['y'],
            srid=4326
        )


class BoatTrackingImporterForm(forms.ModelForm):
    geo_location = CustomPointField()
    lastupdate = forms.DateTimeField(input_formats=['%Y-%m-%dT%H:%M:%S.%fz'])
    lastmoved = forms.DateTimeField(input_formats=['%Y-%m-%dT%H:%M:%S.%fz'], required=False)

    class Meta:
        model = BoatTracking
        fields = list(constants.BOAT_TRACKING_RAW_TO_MODEL_MAPPING.values())
