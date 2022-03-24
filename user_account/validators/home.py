from django.db.models import Q
from quarantine_ward.models import QuarantineWard
from utils import validators, messages, exceptions

class HomeValidator(validators.AbstractRequestValidate):

    def is_valid_fields(self, keys: list):
        ignorable_fields = {}
        set_of_keys = set(keys)

        return super().is_valid_fields(set_of_keys)

    def is_validate_number_of_days_in_out(self):
        if hasattr(self, '_number_of_days_in_out'):
            self._number_of_days_in_out = validators.PositiveIntegerValidator.valid(
                self._number_of_days_in_out,
                message={'number_of_days_in_out': messages.INVALID},
                message1={'number_of_days_in_out': messages.INVALID},
            )

    def is_quarantine_ward_id_exist(self):
        if hasattr(self, '_quarantine_ward_id'):
            try:
                self._quarantine_ward = validators.ModelInstanceExistenceValidator.valid(
                    model_cls=QuarantineWard,
                    query_expr=Q(id=self._quarantine_ward_id),
                )
                return True
            except Exception as exception:
                return False
        else:
            return False

    def extra_validate_to_get_manager_home(self):
        if hasattr(self, '_quarantine_ward_id'):
            if not self.is_quarantine_ward_id_exist():
                raise exceptions.ValidationException({'quarantine_ward_id': messages.NOT_EXIST})
