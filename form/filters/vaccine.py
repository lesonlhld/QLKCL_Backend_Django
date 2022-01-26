import django_filters
from django.db.models import Q
from ..models import VaccineDose

class VaccineDoseFilter(django_filters.FilterSet):

    custom_user_code = django_filters.CharFilter(
        field_name='custom_user__code',
        lookup_expr='iexact',
    )

    injection_date_max = django_filters.DateTimeFilter(
        field_name='injection_date',
        lookup_expr='lte',
    )

    injection_date_min = django_filters.DateTimeFilter(
        field_name='injection_date',
        lookup_expr='gte',
    )

    order_by = django_filters.OrderingFilter(
        fields=(
            ('injection_date', 'injection_date'),
        ),
    )

    search = django_filters.CharFilter(method='query_search')

    def query_search(self, queryset, name, value):
        query = (
            Q(vaccine__name__icontains=value)
        )
        qs = queryset.filter(query)
        return qs

    class Meta:
        model = VaccineDose
        fields = []
