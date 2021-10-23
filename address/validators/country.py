from django.db.models import Q
from ..models import Country
from utils import validators, messages, exceptions

class CountryValidator(validators.AbstractRequestValidate):

    def is_valid_fields(self, keys: list):
        ignorable_fields = {}
        set_of_keys = set(keys)

        return super().is_valid_fields(set_of_keys)

    def is_code_exist(self):
        if hasattr(self, '_code'):
            try:
                self._country = validators.ModelInstanceExistenceValidator.valid(
                    model_cls=Country,
                    query_expr=Q(code=self._code),
                    message={'code': messages.EXIST},
                )
                return True
            except Exception as exception:
                return False
        return False
