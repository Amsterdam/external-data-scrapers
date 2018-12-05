import factory
from django.contrib.gis.geos import Point
from django.utils import timezone
from factory import fuzzy

from ..models import OvFiets

# Amsterdam.
BBOX = [52.03560, 4.58565, 52.48769, 5.31360]


def get_puntje():
    lat = fuzzy.FuzzyFloat(BBOX[0], BBOX[2]).fuzz()
    lon = fuzzy.FuzzyFloat(BBOX[1], BBOX[3]).fuzz()
    return Point(float(lat), float(lon))


class OvFietsFactory(factory.DjangoModelFactory):
    class Meta:
        model = OvFiets

    id = factory.Sequence(lambda n: n)
    name = fuzzy.FuzzyText(length=20)
    station_code = fuzzy.FuzzyText(length=4)
    location_code = fuzzy.FuzzyText(length=7)
    open = fuzzy.FuzzyText(length=7)
    stadsdeel = fuzzy.FuzzyChoice(choices=['A', 'B', 'C'])
    rental_bikes = fuzzy.FuzzyInteger(0, 100)
    fetch_time = fuzzy.FuzzyDateTime(start_dt=timezone.now())
    scraped_at = fuzzy.FuzzyDateTime(start_dt=timezone.now())
    geometrie = get_puntje()
