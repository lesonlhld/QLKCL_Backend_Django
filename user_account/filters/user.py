import datetime
import django_filters
from django.db.models import Q
from ..models import CustomUser, Member
from utils.tools import split_input_list, timestamp_string_to_date_string

class UserFilter(django_filters.FilterSet):

    status = django_filters.CharFilter(
        field_name='status',
        lookup_expr='iexact',
    )

    positive_test = django_filters.CharFilter(
        field_name='member_x_custom_user__positive_test',
        lookup_expr='iexact',
    )

    health_status_list = django_filters.CharFilter(method='health_status_in_list')

    def health_status_in_list(self, queryset, name, value):
        # value in String, not list, so need to convert String to list
        value = split_input_list(value)
        query = (
            Q(member_x_custom_user__health_status__in=value)
        )
        qs = queryset.filter(query)
        return qs

    last_tested = django_filters.DateTimeFilter(
        field_name='member_x_custom_user__last_tested',
        lookup_expr='lte',
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
            Q(code__iexact=value) |
            Q(phone_number__iexact=value)
        )
        qs = queryset.filter(query)
        return qs

    class Meta:
        model = CustomUser
        fields = []
