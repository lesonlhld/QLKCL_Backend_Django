from django.db.models import Q
from ..models import MedicalDeclaration, Test
from user_account.models import CustomUser
from form.models import Symptom
from utils import validators, messages, exceptions
from utils.enums import TestStatus, TestType, TestResult
from utils.tools import split_input_list, date_string_to_timestamp

class TestValidator(validators.AbstractRequestValidate):

    def is_valid_fields(self, keys: list):
        ignorable_fields = {}
        set_of_keys = set(keys)

        return super().is_valid_fields(set_of_keys)

    def is_validate_status(self):
        if hasattr(self, '_status'):
            self._status = validators.EnumValidator.valid(
                value=self._status,
                enum_cls=TestStatus,
                message={'status': messages.INVALID},
            )

    def is_validate_type(self):
        if hasattr(self, '_type'):
            self._type = validators.EnumValidator.valid(
                value=self._type,
                enum_cls=TestType,
                message={'type': messages.INVALID},
            )

    def is_validate_result(self):
        if hasattr(self, '_result'):
            self._result = validators.EnumValidator.valid(
                value=self._result,
                enum_cls=TestResult,
                message={'result': messages.INVALID},
            )

    def is_code_exist(self, code=None):
        if code:
            try:
                validators.ModelInstanceExistenceValidator.valid(
                    model_cls=Test,
                    query_expr=Q(code=code),
                )
                return True
            except Exception as exception:
                return False
        else:
            if hasattr(self, '_code'):
                try:
                    self._test = validators.ModelInstanceExistenceValidator.valid(
                        model_cls=Test,
                        query_expr=Q(code=self._code),
                    )
                    return True
                except Exception as exception:
                    return False
            return False

    def is_user_code_exist(self):
        if hasattr(self, '_user_code'):
            try:
                self._user = validators.ModelInstanceExistenceValidator.valid(
                    model_cls=CustomUser,
                    query_expr=Q(code=self._user_code),
                )
                return True
            except Exception as exception:
                return False
        return False

    def extra_validate_to_create_test(self):
        if hasattr(self, '_user_code') and not self.is_user_code_exist():
            raise exceptions.ValidationException({'user_code': messages.NOT_EXIST})

    def extra_validate_to_get_test(self):
        if hasattr(self, '_code') and not self.is_code_exist():
            raise exceptions.ValidationException({'main': messages.TEST_NOT_FOUND})

    def extra_validate_to_update_test(self):
        if hasattr(self, '_code') and not self.is_code_exist():
            raise exceptions.ValidationException({'main': messages.TEST_NOT_FOUND})

    def extra_validate_to_filter_test(self):
        if hasattr(self, '_user_code') and not self.is_user_code_exist():
            raise exceptions.ValidationException({'main': messages.USER_NOT_FOUND})
        if hasattr(self, '_created_at_max'):
            validators.DateStringValidator.valid(self._created_at_max, message={'created_at_max': messages.INVALID})
            self._created_at_max = date_string_to_timestamp(self._created_at_max, 1)
        if hasattr(self, '_created_at_min'):
            validators.DateStringValidator.valid(self._created_at_min, message={'created_at_min': messages.INVALID})
            self._created_at_min = date_string_to_timestamp(self._created_at_min, 0)
        