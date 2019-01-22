from datapunt_api.rest import HALSerializer

from .models import ThirdpartyTravelTime, TravelTime


class TravelTimeSerializer(HALSerializer):
    class Meta:
        model = TravelTime
        fields = '__all__'


class ThirdpartyTravelTimeSerializer(HALSerializer):
    class Meta:
        model = ThirdpartyTravelTime
        fields = '__all__'
