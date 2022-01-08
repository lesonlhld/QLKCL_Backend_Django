import datetime
from functools import reduce
import operator
import django_filters
from django.db.models import Q
from django.db.models.query import QuerySet
from ..models import CustomUser, Member
from utils.tools import split_input_list

class StaffFilter(django_filters.FilterSet):

    status = django_filters.CharFilter(
        field_name='status',
        lookup_expr='iexact',
    )

    positive_test_now = django_filters.CharFilter(
        field_name='staff_x_custom_user__positive_test_now',
        lookup_expr='iexact',
    )

    health_status_list = django_filters.CharFilter(method='health_status_in_list')

    def health_status_in_list(self, queryset, name, value):
        # value in String, not list, so need to convert String to list
        value = split_input_list(value)
        query = (
            Q(staff_x_custom_user__health_status__in=value)
        )
        qs = queryset.filter(query)
        return qs

    last_tested_max = django_filters.DateTimeFilter(method='query_last_tested_max')

    def query_last_tested_max(self, queryset, name, value):
        query = (
            Q(staff_x_custom_user__last_tested__lte=value) |
            Q(staff_x_custom_user__last_tested=None)
        )
        qs = queryset.filter(query)
        return qs

    quarantine_ward_id = django_filters.CharFilter(
        field_name='quarantine_ward__id',
        lookup_expr='iexact',
    )

    care_area = django_filters.CharFilter(method='care_area_in_list')

    def care_area_in_list(self, queryset, name, value):
        # value in String, not list, so need to convert String to list
        value = split_input_list(value)
        query = reduce(operator.and_, (Q(staff_x_custom_user__care_area__icontains=x) for x in value))
        
        qs = queryset.filter(query)
        return qs

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
            ('full_name', 'full_name'),
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
