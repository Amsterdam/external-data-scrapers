from datapunt_api.rest import DatapuntViewSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter

from .models import ThirdpartyTravelTime, TravelTime

from.serializers import TravelTimeSerializer, ThirdpartyTravelTimeSerializer


class TravelTimeView(DatapuntViewSet):
    queryset = TravelTime.objects.all()

    serializer_detail_class = TravelTimeSerializer
    serializer_class = TravelTimeSerializer

    filter_backends = (
        DjangoFilterBackend,
        OrderingFilter
    )

    filter_fields = [
        'measurement_site_reference',
        'measurement_time',
        'scraped_at'
    ]

    order_fields = ('measurement_time', 'scraped_at')


class ThirdpartyTravelTimeView(DatapuntViewSet):
    queryset = ThirdpartyTravelTime.objects.all()

    serializer_detail_class = ThirdpartyTravelTimeSerializer
    serializer_class = ThirdpartyTravelTimeSerializer

    filter_backends = (
        DjangoFilterBackend,
        OrderingFilter
    )

    filter_fields = [
        'measurement_site_reference',
        'timestamp',
        'scraped_at'
    ]

    order_fields = ('timestamp', 'scraped_at')
