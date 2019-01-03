from django_filters.rest_framework import FilterSet, filters

from .constants import STADSDELEN


class InAmsterdamChoiceFilter(filters.ChoiceFilter):
    """
    Overridden to offer the ability to filter
    with all stations in amsterdam
    """
    def filter(self, qs, value):
        if value == 'in_amsterdam':
            return self.get_method(qs)(stadsdeel__isnull=False)
        return super().filter(qs, value)


class StadsdeelFilter(FilterSet):
    stadsdeel_choices = STADSDELEN + (('in_amsterdam', 'In Amsterdam'),)
    stadsdeel = InAmsterdamChoiceFilter(
        choices=stadsdeel_choices,
        null_label='Not in Amsterdam',
        null_value='null'
    )
