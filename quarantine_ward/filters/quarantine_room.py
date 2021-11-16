import django_filters
from django.db.models import Q
from ..models import QuarantineRoom

class QuarantineRoomFilter(django_filters.FilterSet):

    quarantine_floor = django_filters.CharFilter(
        field_name='quarantine_floor__id',
        lookup_expr='iexact',
    )

    order_by = django_filters.OrderingFilter(
        fields=(
            ('name', 'name'),
        ),
    )

    search = django_filters.CharFilter(method='query_search')

    def query_search(self, queryset, name, value):
        query = (
            Q(name__icontains=value) |
            Q(capacity_iexact=value)
        )
        qs = queryset.filter(query)
        return qs

    class Meta:
        model = QuarantineRoom
        fields = []
