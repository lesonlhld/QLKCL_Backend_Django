from django.db.models import Q
from ..models import City, District
from utils import validators, messages, exceptions

class DistrictValidator(validators.AbstractRequestValidate):

    def is_valid_fields(self, keys: list):
        ignorable_fields = {}
        set_of_keys = set(keys)

        return super().is_valid_fields(set_of_keys)

    def is_city_id_exist(self):
        if hasattr(self, '_city_id'):
            try:
                self._city = validators.ModelInstanceExistenceValidator.valid(
                    model_cls=City,
                    query_expr=Q(id=self._city_id),
                )
                return True
            except Exception as exception:
                return False
        return False

    def extra_validate_to_filter_district(self):
        if hasattr(self, '_city_id') and not self.is_city_id_exist():
            raise exceptions.NotFoundException({'city_id': messages.NOT_EXIST})
