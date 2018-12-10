from datapunt_api.rest import DatapuntViewSet
from django_filters.rest_framework import (DjangoFilterBackend, FilterSet,
                                           filters)
from rest_framework.filters import OrderingFilter

from ..constants import STADSDELEN
from .models import OvFiets
from .serializers import OvFietsDetailSerializer, OvFietsSerializer


class OvFietsChoiceFilter(filters.ChoiceFilter):
    """
    Overridden to offer the ability to filter
    with all stations in amsterdam
    """
    def filter(self, qs, value):
        if value == 'in_amsterdam':
            return self.get_method(qs)(stadsdeel__isnull=False)
        return super().filter(qs, value)


class OVFietsFilter(FilterSet):
    stadsdeel_choices = STADSDELEN + (('in_amsterdam', 'In Amsterdam'),)
    stadsdeel = OvFietsChoiceFilter(
        choices=stadsdeel_choices,
        null_label='Not in Amsterdam',
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
