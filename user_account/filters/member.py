import datetime
import django_filters
from django.db.models import Q
from django.db.models.query import QuerySet
from ..models import CustomUser, Member
from utils.tools import split_input_list, timestamp_string_to_date_string, compare_date_string

class MemberFilter(django_filters.FilterSet):

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

    quarantined_status = django_filters.CharFilter(
        field_name='member_x_custom_user__quarantined_status',
        lookup_expr='iexact',
    )

    quarantined_status_list = django_filters.CharFilter(method='quarantined_status_in_list')

    def quarantined_status_in_list(self, queryset, name, value):
        # value in String, not list, so need to convert String to list
        # value is VD: 'HOSPITALIZE,MOVED'
        value = split_input_list(value)
        query = (
            Q(member_x_custom_user__quarantined_status__in=value)
        )
        qs = queryset.filter(query)
        return qs

    positive_test_now = django_filters.CharFilter(
        field_name='member_x_custom_user__positive_test_now',
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
                Q(member_x_custom_user__positive_test_now__in=value) |
                Q(member_x_custom_user__positive_test_now__isnull=True)
            )
        else:
            query = (
                Q(member_x_custom_user__positive_test_now__in=value)
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
                Q(member_x_custom_user__health_status__in=value) |
                Q(member_x_custom_user__health_status__isnull=True)
            )
        else:
            query = (
                Q(member_x_custom_user__health_status__in=value)
            )
        qs = queryset.filter(query)
        return qs

    label_list = django_filters.CharFilter(method='label_in_list')

    def label_in_list(self, queryset, name, value):
        # value in String, not list, so need to convert String to list
        value = split_input_list(value)
        query = (
            Q(member_x_custom_user__label__in=value)
        )
        qs = queryset.filter(query)
        return qs

    last_tested_max = django_filters.DateTimeFilter(method='query_last_tested_max')

    def query_last_tested_max(self, queryset, name, value):
        query = (
            Q(member_x_custom_user__last_tested__lte=value) |
            Q(member_x_custom_user__last_tested=None)
        )
        qs = queryset.filter(query)
        return qs

    quarantined_at_max = django_filters.DateTimeFilter(
        field_name='member_x_custom_user__quarantined_at',
        lookup_expr='lte',
    )

    quarantined_at_min = django_filters.DateTimeFilter(
        field_name='member_x_custom_user__quarantined_at',
        lookup_expr='gte',
    )

    quarantined_finish_expected_at_max = django_filters.DateTimeFilter(
        field_name='member_x_custom_user__quarantined_finish_expected_at',
        lookup_expr='lte',
    )

    quarantined_finish_expected_at_min = django_filters.DateTimeFilter(
        field_name='member_x_custom_user__quarantined_finish_expected_at',
        lookup_expr='gte',
    )

    quarantined_finished_at_max = django_filters.DateTimeFilter(
        field_name='member_x_custom_user__quarantined_finished_at',
        lookup_expr='lte',
    )

    quarantined_finished_at_min = django_filters.DateTimeFilter(
        field_name='member_x_custom_user__quarantined_finished_at',
        lookup_expr='gte',
    )

    quarantine_ward_id = django_filters.CharFilter(
        field_name='quarantine_ward__id',
        lookup_expr='iexact',
    )

    quarantine_building_id = django_filters.CharFilter(
        field_name='member_x_custom_user__quarantine_room__quarantine_floor__quarantine_building__id',
        lookup_expr='iexact',
    )

    quarantine_floor_id = django_filters.CharFilter(
        field_name='member_x_custom_user__quarantine_room__quarantine_floor__id',
        lookup_expr='iexact',
    )

    quarantine_room_id = django_filters.CharFilter(
        field_name='member_x_custom_user__quarantine_room__id',
        lookup_expr='iexact',
    )

    label = django_filters.CharFilter(
        field_name='member_x_custom_user__label',
        lookup_expr='iexact',
    )

    care_staff_code = django_filters.CharFilter(
        field_name='member_x_custom_user__care_staff__code',
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
            ('member_x_custom_user__quarantined_at', 'quarantined_at'),
            ('created_at', 'created_at'),
            ('member_x_custom_user__quarantined_finished_at', 'quarantined_finished_at')
        ),
    )

    search = django_filters.CharFilter(method='query_search')

    def query_search(self, queryset, name, value):
        query = (
            Q(full_name__icontains=value) |
            Q(full_name__unaccent__icontains=value) |
            Q(code__iexact=value) |
            Q(phone_number__iexact=value) |
            Q(identity_number__iexact=value)
        )
        qs = queryset.filter(query)
        return qs

    class Meta:
        model = CustomUser
        fields = []
