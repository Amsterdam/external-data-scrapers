import factory
from django.contrib.gis.geos import LineString
from django.utils import timezone
from factory import fuzzy

from ..models import ThirdpartyTravelTime, TravelTime

# Amsterdam.
BBOX = [52.03560, 4.58565, 52.48769, 5.31360]


def get_puntje():
    linestring = []
    for _ in range(3):
        lat = fuzzy.FuzzyFloat(BBOX[0], BBOX[2]).fuzz()
        lon = fuzzy.FuzzyFloat(BBOX[1], BBOX[3]).fuzz()
        linestring.append((lat, lon))
    return LineString(linestring)


class TravelTimeFactory(factory.DjangoModelFactory):
    class Meta:
        model = TravelTime

    measurement_site_reference = fuzzy.FuzzyText(length=30)
    number_of_incomplete_input = fuzzy.FuzzyInteger(0, 100)
    number_of_input_values_used = fuzzy.FuzzyInteger(0, 100)
    standard_deviation = fuzzy.FuzzyFloat(0.0, 100.0)
    supplier_calculated_data_quality = fuzzy.FuzzyFloat(0.0, 100.0)
    duration = fuzzy.FuzzyFloat(0.0, 100.0)
    measurement_time = fuzzy.FuzzyDateTime(start_dt=timezone.now())
    scraped_at = fuzzy.FuzzyDateTime(start_dt=timezone.now())


class ThirdpartyTravelTimeFactory(factory.DjangoModelFactory):
    class Meta:
        model = ThirdpartyTravelTime

    measurement_site_reference = fuzzy.FuzzyText(length=30)
    name = fuzzy.FuzzyText(length=30)
    type = fuzzy.FuzzyText(length=2)
    length = fuzzy.FuzzyInteger(0, 100)
    geometrie = get_puntje()
    timestamp = fuzzy.FuzzyDateTime(start_dt=timezone.now())
    scraped_at = fuzzy.FuzzyDateTime(start_dt=timezone.now())
