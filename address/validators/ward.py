from django.db.models import Q
from ..models import District, Ward
from utils import validators, messages, exceptions

class WardValidator(validators.AbstractRequestValidate):

    def is_valid_fields(self, keys: list):
        ignorable_fields = {}
        set_of_keys = set(keys)

        return super().is_valid_fields(set_of_keys)

    def is_district_id_exist(self):
        if hasattr(self, '_district_id'):
            try:
                self._district = validators.ModelInstanceExistenceValidator.valid(
                    model_cls=District,
                    query_expr=Q(id=self._district_id),
                )
                return True
            except Exception as exception:
                return False
        return False

    def extra_validate_to_filter_ward(self):
        if hasattr(self, '_district_id') and not self.is_district_id_exist():
            raise exceptions.NotFoundException({'district_id': messages.NOT_EXIST})
