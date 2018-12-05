from datapunt_api.rest import DatapuntViewSet
from django_filters.rest_framework import (DjangoFilterBackend, FilterSet,
                                           filters)
from rest_framework.filters import OrderingFilter

from ..constants import STADSDELEN
from .models import OvFiets
from .serializers import OvFietsDetailSerializer, OvFietsSerializer


class OVFietsFilter(FilterSet):
    stadsdeel = filters.MultipleChoiceFilter(
        choices=STADSDELEN,
        null_label='not_in_amsterdam',
        null_value='null'
    )

    class Meta(object):
        model = OvFiets
        fields = (
            'station_code',
            'location_code',
            'stadsdeel',
            'open'
        )


class OvFietsView(DatapuntViewSet):
    queryset = (
        OvFiets.objects.all()
    )
    serializer_detail_class = OvFietsDetailSerializer
    serializer_class = OvFietsSerializer

    filter_backends = (
        DjangoFilterBackend,
        OrderingFilter
    )

    filterset_class = OVFietsFilter

    ordering_fields = '__all__'
