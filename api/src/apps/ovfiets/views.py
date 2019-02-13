from datapunt_api.pagination import HALCursorPagination
from datapunt_api.rest import DatapuntViewSet
from django_filters.rest_framework import DjangoFilterBackend

from ..filters import StadsdeelFilter
from .models import OvFiets
from .serializers import OvFietsDetailSerializer, OvFietsSerializer


class OVFietsFilter(StadsdeelFilter):
    class Meta:
        model = OvFiets
        fields = (
            'station_code',
            'location_code',
            'stadsdeel',
            'open'
        )


class OvFietsCursorPagination(HALCursorPagination):
    """
    Ovfiets entries are too many. So we use cursor based pagination.
    """
    page_size = 1000
    max_page_size = 1000
    ordering = "-scraped_at"
    count_table = False


class OvFietsView(DatapuntViewSet):
    queryset = (
        OvFiets.objects.all()
    )
    serializer_detail_class = OvFietsDetailSerializer
    serializer_class = OvFietsSerializer
    pagination_class = OvFietsCursorPagination

    filter_backends = (
        DjangoFilterBackend,
    )

    filterset_class = OVFietsFilter
