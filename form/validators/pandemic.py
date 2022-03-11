from django.db.models import Q
from ..models import Pandemic
from utils import validators, messages, exceptions
from utils.enums import TestStatus, TestType, TestResult

class PandemicValidator(validators.AbstractRequestValidate):

    def is_valid_fields(self, keys: list):
        ignorable_fields = {}
        set_of_keys = set(keys)

        return super().is_valid_fields(set_of_keys)

    def is_name_exist(self):
        if hasattr(self, '_name'):
            try:
                self._pandemic = validators.ModelInstanceExistenceValidator.valid(
                    model_cls=Pandemic,
                    query_expr=Q(name=self._name),
                )
                return True
            except Exception as exception:
                return False
        return False

    def extra_validate_to_create_pandemic(self):
        if hasattr(self, '_name') and self._name:
            if self.is_name_exist():
                raise exceptions.ValidationException({'name': messages.EXIST})
