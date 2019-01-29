from datapunt_api.rest import DatapuntViewSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter

from .models import TravelTime
from .serializers import TravelTimeSerializer


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
