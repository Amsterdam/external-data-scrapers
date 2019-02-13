from datapunt_api.rest import HALSerializer
from rest_framework import serializers

from .models import OvFiets


class OvFietsSerializer(HALSerializer):
    class Meta:
        model = OvFiets
        fields = (
            '_links',
            'id',
            'name',
            'description',
            'station_code',
            'location_code',
            'open',
            'geometrie',
            'rental_bikes',
            'fetch_time',
            'scraped_at',
            'stadsdeel'
        )


class OvFietsDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = OvFiets
        fields = '__all__'
