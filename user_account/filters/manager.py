import datetime
from functools import reduce
import operator
import django_filters
from django.db.models import Q
from django.db.models.query import QuerySet
from ..models import CustomUser, Member
from utils.tools import split_input_list

class ManagerFilter(django_filters.FilterSet):

    status = django_filters.CharFilter(
        field_name='status',
        lookup_expr='iexact',
    )

    status_list = django_filters.CharFilter(method='status_in_list')

    def status_in_list(self, queryset, name, value):
        # value in String, not list, so need to convert String to list
        # value is VD: 'AVAILABLE,WAITING,LEAVE'
        value = split_input_list(value)
        query = (
            Q(status__in=value)
        )
        qs = queryset.filter(query)
        return qs

    positive_test_now = django_filters.CharFilter(
        field_name='staff_x_custom_user__positive_test_now',
        lookup_expr='iexact',
    )

    positive_test_now_list = django_filters.CharFilter(method='positive_test_now_in_list')

    def positive_test_now_in_list(self, queryset, name, value):
        # value in String, not list, so need to convert String to list
        # value is VD: '[False, True, False, True, None]'
        value = value[1:-1]
        value = split_input_list(value)

        new_value = []
        for item in value:
            if item == 'True':
                new_value += [True]
            elif item == 'False':
                new_value += [False]
            elif item == 'None':
                new_value += [None]
        value = new_value
        
        if None in value:
            query = (
                Q(staff_x_custom_user__positive_test_now__in=value) |
                Q(staff_x_custom_user__positive_test_now__isnull=True)
            )
        else:
            query = (
                Q(staff_x_custom_user__positive_test_now__in=value)
            )
        qs = queryset.filter(query)
        return qs

    health_status_list = django_filters.CharFilter(method='health_status_in_list')

    def health_status_in_list(self, queryset, name, value):
        # value in String, not list, so need to convert String to list
        # value is VD: 'NORMAL,UNWELL,SERIOUS,Null'
        value = split_input_list(value)
        if 'Null' in value:
            query = (
                Q(staff_x_custom_user__health_status__in=value) |
                Q(staff_x_custom_user__health_status__isnull=True)
            )
        else:
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

    role_name = django_filters.CharFilter(
        field_name='role__name',
        lookup_expr='iexact',
    )

    role_name_list = django_filters.CharFilter(method='role_name_in_list')

    def role_name_in_list(self, queryset, name, value):
        # value in String, not list, so need to convert String to list
        # value is VD: 'MANAGER,SUPER_MANAGER'
        value = split_input_list(value)
        query = (
            Q(role__name__in=value)
        )
        qs = queryset.filter(query)
        return qs

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
            Q(full_name__unaccent__icontains=value) |
            Q(code__iexact=value) |
            Q(phone_number__iexact=value)
        )
        qs = queryset.filter(query)
        return qs

    class Meta:
        model = CustomUser
        fields = []
