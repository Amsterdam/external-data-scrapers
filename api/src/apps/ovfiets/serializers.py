from datapunt_api.rest import HALSerializer
from rest_framework import serializers

from .models import OvFiets


class OvFietsSerializer(HALSerializer):
    name = serializers.CharField()
    description = serializers.CharField()
    station_code = serializers.CharField()
    location_code = serializers.CharField()
    open = serializers.CharField()
    geometrie = serializers.CharField()
    stadsdeel = serializers.CharField()
    rental_bikes = serializers.IntegerField()
    fetch_time = serializers.DateTimeField()
    scraped_at = serializers.DateTimeField()

    class Meta(object):
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
    class Meta(object):
        model = OvFiets
        fields = '__all__'
