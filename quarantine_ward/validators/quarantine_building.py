from ..models import QuarantineWard, QuarantineBuilding
from utils import validators, messages
from django.db.models import Q

class QuarantineBuildingValidator(validators.AbstractRequestValidate):

    def is_valid_fields(self, keys: list):
        ignorable_fields = {'name',
                            }
        set_of_keys = set(keys) - ignorable_fields

        return super().is_valid_fields(set_of_keys)

    def is_validate_quarantine_ward(self):
        self._quarantine_ward = validators.ModelInstanceExistenceValidator.valid(
            model_cls=QuarantineWard,
            query_expr=Q(
                id=self._quarantine_ward,
            ),
            message=messages.QUARANTINE_WARD_NOT_FOUND,
        )
    
    def is_validate_id(self):
        self._id = validators.ModelInstanceExistenceValidator.valid(
            model_cls=QuarantineBuilding,
            query_expr=Q(
                id=self._id,
            ),
            message=messages.QUARANTINE_BUILDING_NOT_FOUND,
        )

