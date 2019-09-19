from django.contrib.gis import forms, geos
from django.utils import timezone

from apps.ovfiets import constants
from apps.ovfiets.models import OvFiets


class CustomTimestampField(forms.DateTimeField):
    def to_python(self, value):
        return timezone.datetime.fromtimestamp(value, tz=timezone.utc)


class CustomGeometryField(forms.PointField):
    def to_python(self, value):
        return geos.Point(
            value[0],
            value[1],
            srid=4326
        )


class OvFietsImporterForm(forms.ModelForm):
    fetch_time = CustomTimestampField()
    geometrie = CustomGeometryField()

    class Meta:
        model = OvFiets
        fields = constants.OVFIETS_FORM_FIELDS
