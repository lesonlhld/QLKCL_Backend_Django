from django.db.models import Q
from ..models import City, Country
from utils import validators, messages, exceptions

class CityValidator(validators.AbstractRequestValidate):

    def is_valid_fields(self, keys: list):
        ignorable_fields = {}
        set_of_keys = set(keys)

        return super().is_valid_fields(set_of_keys)

    def is_country_code_exist(self):
        if hasattr(self, '_country_code'):
            try:
                self._country = validators.ModelInstanceExistenceValidator.valid(
                    model_cls=Country,
                    query_expr=Q(code=self._country_code),
                )
                return True
            except Exception as exception:
                return False
        return False

    def extra_validate_to_filter_city(self):
        if hasattr(self, '_country_code') and not self.is_country_code_exist():
            raise exceptions.NotFoundException({'country_code': messages.NOT_EXIST})
