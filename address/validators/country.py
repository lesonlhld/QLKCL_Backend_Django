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
                self._country = Country.objects.get(code=self._code)
                return True
            except Exception as exception:
                return False
        return False
