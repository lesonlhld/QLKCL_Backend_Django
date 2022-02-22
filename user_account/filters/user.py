import django_filters
from django.db.models import Q
from ..models import CustomUser
from utils.tools import split_input_list

class UserFilter(django_filters.FilterSet):

    status = django_filters.CharFilter(
        field_name='status',
        lookup_expr='iexact',
    )

    quarantine_ward_id = django_filters.CharFilter(
        field_name='quarantine_ward__id',
        lookup_expr='iexact',
    )

    role_name_list = django_filters.CharFilter(method='role_name_in_list')

    def role_name_in_list(self, queryset, name, value):
        # value in String, not list, so need to convert String to list
        value = split_input_list(value)
        query = (
            Q(role__name__in=value)
        )
        qs = queryset.filter(query)
        return qs
    
    class Meta:
        model = CustomUser
        fields = []
