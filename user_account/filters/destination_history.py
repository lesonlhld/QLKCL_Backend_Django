import django_filters
from django.db.models import Q
from ..models import DestinationHistory

class DestinationHistoryFilter(django_filters.FilterSet):

    user_code = django_filters.CharFilter(
        field_name='user__code',
        lookup_expr='iexact',
    )

    order_by = django_filters.OrderingFilter(
        fields=(
            ('start_time', 'start_time'),
        ),
    )
    
    class Meta:
        model = DestinationHistory
        fields = []
