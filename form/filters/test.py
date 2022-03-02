import django_filters
from django.db.models import Q
from ..models import Test

class TestFilter(django_filters.FilterSet):

    user_code = django_filters.CharFilter(
        field_name='user__code',
        lookup_expr='iexact',
    )

    status = django_filters.CharFilter(
        field_name='status',
        lookup_expr='iexact',
    )

    result = django_filters.CharFilter(
        field_name='result',
        lookup_expr='iexact',
    )

    type = django_filters.CharFilter(
        field_name='type',
        lookup_expr='iexact',
    )

    created_at_min = django_filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='gte',
    )

    created_at_max = django_filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='lte',
    )

    updated_at_min = django_filters.DateTimeFilter(
        field_name='updated_at',
        lookup_expr='gte',
    )

    updated_at_max = django_filters.DateTimeFilter(
        field_name='updated_at',
        lookup_expr='lte',
    )

    order_by = django_filters.OrderingFilter(
        fields=(
            ('created_at', 'created_at'),
            ('updated_at', 'updated_at'),
        ),
    )

    search = django_filters.CharFilter(method='query_search')

    def query_search(self, queryset, name, value):
        query = (
            Q(user__full_name__icontains=value) |
            Q(user__full_name__unaccent__icontains=value) |
            Q(code__iexact=value)
        )
        qs = queryset.filter(query)
        return qs

    class Meta:
        model = Test
        fields = []
