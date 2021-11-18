import datetime
import django_filters
from django.db.models import Q
from django.db.models.query import QuerySet
from ..models import CustomUser, Member
from utils.tools import split_input_list, timestamp_string_to_date_string, compare_date_string

class UserFilter(django_filters.FilterSet):

    status = django_filters.CharFilter(
        field_name='status',
        lookup_expr='iexact',
    )

    quarantined_status = django_filters.CharFilter(
        field_name='member_x_custom_user__quarantined_status',
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

    role_name_list = django_filters.CharFilter(method='role_name_in_list')

    def role_name_in_list(self, queryset, name, value):
        # value in String, not list, so need to convert String to list
        value = split_input_list(value)
        query = (
            Q(role__name__in=value)
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

    quarantined_at_max = django_filters.CharFilter(field_name='member_x_custom_user__quarantined_at', method='query_quarantined_at_max')

    def query_quarantined_at_max(self, queryset, name, value):
        new_query_set = queryset.exclude()

        for custom_user in queryset:
            if hasattr(custom_user, 'member_x_custom_user'):
                date = custom_user.member_x_custom_user.quarantined_at
                if date:
                    if compare_date_string(date, value) != 1:
                        continue
            new_query_set = new_query_set.exclude(id=custom_user.id)

        return new_query_set

    quarantined_at_min = django_filters.CharFilter(field_name='member_x_custom_user__quarantined_at', method='query_quarantined_at_min')

    def query_quarantined_at_min(self, queryset, name, value):
        new_query_set = queryset.exclude()

        for custom_user in queryset:
            if hasattr(custom_user, 'member_x_custom_user'):
                date = custom_user.member_x_custom_user.quarantined_at
                if date:
                    if compare_date_string(date, value) != -1:
                        continue
            new_query_set = new_query_set.exclude(id=custom_user.id)

        return new_query_set

    quarantined_finished_at_max = django_filters.CharFilter(field_name='member_x_custom_user__quarantined_finished_at', method='query_quarantined_finished_at_max')

    def query_quarantined_finished_at_max(self, queryset, name, value):
        new_query_set = queryset.exclude()

        for custom_user in queryset:
            if hasattr(custom_user, 'member_x_custom_user'):
                date = custom_user.member_x_custom_user.quarantined_finished_at
                if date:
                    if compare_date_string(date, value) != 1:
                        continue
            new_query_set = new_query_set.exclude(id=custom_user.id)

        return new_query_set

    quarantined_finished_at_min = django_filters.CharFilter(field_name='member_x_custom_user__quarantined_finished_at', method='query_quarantined_finished_at_min')

    def query_quarantined_finished_at_min(self, queryset, name, value):
        new_query_set = queryset.exclude()

        for custom_user in queryset:
            if hasattr(custom_user, 'member_x_custom_user'):
                date = custom_user.member_x_custom_user.quarantined_finished_at
                if date:
                    if compare_date_string(date, value) != -1:
                        continue
            new_query_set = new_query_set.exclude(id=custom_user.id)

        return new_query_set

    quarantine_ward_id = django_filters.CharFilter(
        field_name='member_x_custom_user__quarantine_room__quarantine_floor__quarantine_building__quarantine_ward__id',
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

    abroad = django_filters.CharFilter(
        field_name='member_x_custom_user__abroad',
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
            Q(code__iexact=value) |
            Q(phone_number__iexact=value)
        )
        qs = queryset.filter(query)
        return qs

    class Meta:
        model = CustomUser
        fields = []
