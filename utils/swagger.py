from drf_yasg.inspectors.base import FilterInspector, PaginatorInspector
from drf_yasg.utils import force_real_str
from drf_yasg import openapi
import coreschema
from collections import OrderedDict

class CustomCoreAPICompatInspector(FilterInspector, PaginatorInspector):
    def get_paginator_parameters(self, paginator):
        fields = []
        if hasattr(paginator, 'get_schema_fields'):
            fields = paginator.get_schema_fields(self.view)

        return [self.coreapi_field_to_parameter(field) for field in fields]

    def get_filter_parameters(self, filter_backend):
        fields = []
        if hasattr(filter_backend, 'get_schema_fields'):
            fields = filter_backend.get_schema_fields(self.view)
        return []
        return [self.coreapi_field_to_parameter(field) for field in fields]

    def coreapi_field_to_parameter(self, field):
        """Convert an instance of `coreapi.Field` to a swagger :class:`.Parameter` object.
        :param coreapi.Field field:
        :rtype: openapi.Parameter
        """
        location_to_in = {
            'query': openapi.IN_QUERY,
            'path': openapi.IN_PATH,
            'form': openapi.IN_FORM,
            'body': openapi.IN_FORM,
        }
        coreapi_types = {
            coreschema.Integer: openapi.TYPE_INTEGER,
            coreschema.Number: openapi.TYPE_NUMBER,
            coreschema.String: openapi.TYPE_STRING,
            coreschema.Boolean: openapi.TYPE_BOOLEAN,
        }

        coreschema_attrs = ['format', 'pattern', 'enum', 'min_length', 'max_length']
        schema = field.schema
        return openapi.Parameter(
            name=field.name,
            in_=location_to_in[field.location],
            required=field.required,
            description=force_real_str(schema.description) if schema else None,
            type=coreapi_types.get(type(schema), openapi.TYPE_STRING),
            **OrderedDict((attr, getattr(schema, attr, None)) for attr in coreschema_attrs)
        )
