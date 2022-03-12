from django.db.models import Q
from ..models import Pandemic
from utils import validators, messages, exceptions
from utils.enums import TestStatus, TestType, TestResult

class PandemicValidator(validators.AbstractRequestValidate):

    def is_valid_fields(self, keys: list):
        ignorable_fields = {}
        set_of_keys = set(keys)

        return super().is_valid_fields(set_of_keys)

    def is_id_exist(self):
        if hasattr(self, '_id'):
            try:
                self._pandemic = validators.ModelInstanceExistenceValidator.valid(
                    model_cls=Pandemic,
                    query_expr=Q(id=self._id),
                )
                return True
            except Exception as exception:
                return False
        return False

    def is_name_exist(self):
        if hasattr(self, '_name'):
            try:
                validators.ModelInstanceExistenceValidator.valid(
                    model_cls=Pandemic,
                    query_expr=Q(name=self._name),
                )
                return True
            except Exception as exception:
                return False
        return False

    def is_new_name_exist(self):
        if hasattr(self, '_name'):
            try:
                this_pandemic = validators.ModelInstanceExistenceValidator.valid(
                    model_cls=Pandemic,
                    query_expr=Q(name=self._name),
                )
                if this_pandemic != self._pandemic:
                    return True
                else:
                    return False
            except Exception as exception:
                return False
        return False

    def extra_validate_positive_integer(self, list):
        for item in list:
            if hasattr(self, f'_{item}'):
                setattr(self,
                    f'_{item}',
                    validators.PositiveIntegerValidator.valid(
                        value=getattr(self, f'_{item}'),
                        message={item: messages.INVALID},
                        message1={item: messages.INVALID},
                    )
                )

    def extra_validate_test_type(self, list):
        for item in list:
            if hasattr(self, f'_{item}'):
                setattr(self,
                    f'_{item}',
                    validators.EnumValidator.valid(
                        value=getattr(self, f'_{item}'),
                        enum_cls=TestType,
                        message={item: messages.INVALID},
                    )
                )

    def extra_validate_to_create_pandemic(self):
        if hasattr(self, '_name') and self._name:
            if self.is_name_exist():
                raise exceptions.ValidationException({'name': messages.EXIST})

    def extra_validate_to_get_pandemic(self):
        if hasattr(self, '_id') and self._id:
            if not self.is_id_exist():
                raise exceptions.ValidationException({'id': messages.NOT_EXIST})

    def extra_validate_to_update_pandemic(self):
        if hasattr(self, '_id') and self._id:
            if not self.is_id_exist():
                raise exceptions.ValidationException({'id': messages.NOT_EXIST})
        if hasattr(self, '_name') and self._name:
            if self.is_new_name_exist():
                raise exceptions.ValidationException({'name': messages.EXIST})
