from django.db.models import Q
from ..models import MedicalDeclaration, Test
from user_account.models import CustomUser
from form.models import Symptom
from utils import validators, messages, exceptions
from utils.enums import TestStatus, TestType, TestResult
from utils.tools import split_input_list

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

    def is_id_exist(self):
        if hasattr(self, '_id'):
            try:
                self._test = validators.ModelInstanceExistenceValidator.valid(
                    model_cls=Test,
                    query_expr=Q(id=self._id),
                )
                return True
            except Exception as exception:
                return False
        return False

    def is_user_id_exist(self):
        if hasattr(self, '_user_id'):
            try:
                self._user = validators.ModelInstanceExistenceValidator.valid(
                    model_cls=CustomUser,
                    query_expr=Q(id=self._user_id),
                )
                return True
            except Exception as exception:
                return False
        return False

    def extra_validate_to_create_test(self):
        if hasattr(self, '_user_id') and not self.is_user_id_exist():
            raise exceptions.ValidationException({'user_id': messages.NOT_EXIST})

    def extra_validate_to_get_test(self):
        if hasattr(self, '_id') and not self.is_id_exist():
            raise exceptions.ValidationException({'main': messages.TEST_NOT_FOUND})
