import django_filters
from django.db.models import Q
from ..models import QuarantineWard

class QuarantineWardFilter(django_filters.FilterSet):

    country = django_filters.CharFilter(
        field_name='country__code',
        lookup_expr='iexact',
    )

    city = django_filters.CharFilter(
        field_name='city__id',
        lookup_expr='iexact',
    )

    district = django_filters.CharFilter(
        field_name='district__id',
        lookup_expr='iexact',
    )

    ward = django_filters.CharFilter(
        field_name='ward__id',
        lookup_expr='iexact',
    )

    main_manager = django_filters.CharFilter(
        field_name='main_manager__code',
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
            Q(full_name__icontains=value)
        )
        qs = queryset.filter(query)
        return qs

    class Meta:
        model = QuarantineWard
        fields = []
