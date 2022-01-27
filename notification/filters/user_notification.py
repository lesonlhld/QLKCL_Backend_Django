import django_filters
from django.db.models import Q
from ..models import UserNotification

class UserNotificationFilter(django_filters.FilterSet):

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

    class Meta:
        model = UserNotification
        fields = []
