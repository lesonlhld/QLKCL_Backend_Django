from drf_yasg import openapi

from utils.enums import TestType

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
    openapi.Parameter('remain_qt_cc_not_pos_vac', in_=openapi.IN_FORM, type=openapi.TYPE_NUMBER),
    openapi.Parameter('remain_qt_cc_not_pos_not_vac', in_=openapi.IN_FORM, type=openapi.TYPE_NUMBER),
    openapi.Parameter('remain_qt_pos_vac', in_=openapi.IN_FORM, type=openapi.TYPE_NUMBER),
    openapi.Parameter('remain_qt_pos_not_vac', in_=openapi.IN_FORM, type=openapi.TYPE_NUMBER),
    openapi.Parameter('test_type_pos_to_neg_vac', in_=openapi.IN_FORM, type=openapi.TYPE_STRING, enum=list(TestType.__members__.values())),
    openapi.Parameter('num_test_pos_to_neg_vac', in_=openapi.IN_FORM, type=openapi.TYPE_NUMBER),
    openapi.Parameter('test_type_pos_to_neg_not_vac', in_=openapi.IN_FORM, type=openapi.TYPE_STRING, enum=list(TestType.__members__.values())),
    openapi.Parameter('num_test_pos_to_neg_not_vac', in_=openapi.IN_FORM, type=openapi.TYPE_NUMBER),
    openapi.Parameter('test_type_none_to_neg_vac', in_=openapi.IN_FORM, type=openapi.TYPE_STRING, enum=list(TestType.__members__.values())),
    openapi.Parameter('num_test_none_to_neg_vac', in_=openapi.IN_FORM, type=openapi.TYPE_NUMBER),
    openapi.Parameter('test_type_none_to_neg_not_vac', in_=openapi.IN_FORM, type=openapi.TYPE_STRING, enum=list(TestType.__members__.values())),
    openapi.Parameter('num_test_none_to_neg_not_vac', in_=openapi.IN_FORM, type=openapi.TYPE_NUMBER),
    openapi.Parameter('num_day_to_close_room', in_=openapi.IN_FORM, type=openapi.TYPE_NUMBER),
    openapi.Parameter('day_between_tests', in_=openapi.IN_FORM, type=openapi.TYPE_NUMBER),
]