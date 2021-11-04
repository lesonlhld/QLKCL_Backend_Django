import django_filters
from django.db.models import Q
from ..models import CustomUser, Member

class UserFilter(django_filters.FilterSet):

    status = django_filters.CharFilter(
        field_name='status',
        lookup_expr='iexact',
    )

    role_name = django_filters.CharFilter(
        field_name='role__name',
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

    order_by = django_filters.OrderingFilter(
        fields=(
            ('created_at', 'created_at'),
        ),
    )

    search = django_filters.CharFilter(method='query_search')

    def query_search(self, queryset, name, value):
        query = (
            Q(full_name__icontains=value) |
            Q(code__iexact=value)
        )
        qs = queryset.filter(query)
        return qs

    class Meta:
        model = CustomUser
        fields = []
