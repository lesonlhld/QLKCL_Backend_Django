import datetime
import django_filters
from django.db.models import Q
from django.db.models.query import QuerySet
from ..models import City
from utils.tools import split_input_list, timestamp_string_to_date_string, compare_date_string

class CityFilter(django_filters.FilterSet):

    country_code = django_filters.CharFilter(
        field_name='country__code',
        lookup_expr='iexact',
    )

    search = django_filters.CharFilter(method='query_search')

    def query_search(self, queryset, name, value):
        query = (
            Q(name__icontains=value)
        )
        qs = queryset.filter(query)
        return qs

    class Meta:
        model = City
        fields = []