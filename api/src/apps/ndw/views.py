from datapunt_api.pagination import HALCursorPagination
from datapunt_api.rest import DatapuntViewSet
from django_filters.rest_framework import DjangoFilterBackend

from ..filters import StadsdeelFilter
from .models import TravelTime
from .serializers import TravelTimeSerializer


class TravelTimeFilter(StadsdeelFilter):
    class Meta:
        model = TravelTime
        fields = (
            'measurement_site_reference',
            'measurement_time',
            'scraped_at',
            'stadsdeel',
            'buurt_code'
        )


class TravelTimeCursorPagination(HALCursorPagination):
    """
    Traveltime entries are too many. So we use cursor based pagination.
    """
    page_size = 1000
    max_page_size = 1000
    ordering = "-scraped_at"
    count_table = False


class TravelTimeView(DatapuntViewSet):
    queryset = TravelTime.objects.all()

    serializer_detail_class = TravelTimeSerializer
    serializer_class = TravelTimeSerializer
    pagination_class = TravelTimeCursorPagination

    filter_backends = (
        DjangoFilterBackend,
    )

    filterset_class = TravelTimeFilter
