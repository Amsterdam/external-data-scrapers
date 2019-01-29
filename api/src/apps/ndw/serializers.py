from datapunt_api.rest import HALSerializer

from .models import TravelTime


class TravelTimeSerializer(HALSerializer):
    class Meta:
        model = TravelTime
        fields = '__all__'
