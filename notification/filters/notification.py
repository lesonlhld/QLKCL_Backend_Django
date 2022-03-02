import django_filters
from django.db.models import Q
from ..models import Notification

class NotificationFilter(django_filters.FilterSet):

    created_at_min = django_filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='gte',
    )

    created_at_max = django_filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='lte',
    )

    order_by = django_filters.OrderingFilter(
        fields=(
            ('created_at', 'created_at'),
        ),
    )

    search = django_filters.CharFilter(method='query_search')

    def query_search(self, queryset, name, value):
        query = (
            Q(title__icontains=value) |
            Q(title__unaccent__icontains=value)
        )
        qs = queryset.filter(query)
        return qs

    class Meta:
        model = Notification
        fields = []
