import django_filters
from django.db.models import Q
from ..models import QuarantineHistory

class QuarantineHistoryFilter(django_filters.FilterSet):

    user_code = django_filters.CharFilter(
        field_name='user__code',
        lookup_expr='iexact',
    )

    order_by = django_filters.OrderingFilter(
        fields=(
            ('start_date', 'start_date'),
        ),
    )
    
    class Meta:
        model = QuarantineHistory
        fields = []
