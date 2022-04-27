from drf_yasg import openapi

# Pandemic

get_pandemic_swagger_params = [
    openapi.Parameter('id', in_=openapi.IN_FORM, type=openapi.TYPE_NUMBER, required=True),
]

update_pandemic_swagger_params = [
    openapi.Parameter('id', in_=openapi.IN_FORM, type=openapi.TYPE_NUMBER, required=True),
    openapi.Parameter('name', in_=openapi.IN_FORM, type=openapi.TYPE_STRING),
    openapi.Parameter('quarantine_time_not_vac', in_=openapi.IN_FORM, type=openapi.TYPE_NUMBER),
    openapi.Parameter('quarantine_time_vac', in_=openapi.IN_FORM, type=openapi.TYPE_NUMBER),
    openapi.Parameter('remain_qt_cc_pos_vac', in_=openapi.IN_FORM, type=openapi.TYPE_NUMBER),
    openapi.Parameter('remain_qt_cc_pos_not_vac', in_=openapi.IN_FORM, type=openapi.TYPE_NUMBER),
]