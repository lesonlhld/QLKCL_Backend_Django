from ..models import QuarantineWard, QuarantineBuilding
from utils import validators, messages, exceptions
from django.db.models import Q
from utils.tools import date_string_to_timestamp

class QuarantineBuildingValidator(validators.AbstractRequestValidate):

    def is_valid_fields(self, keys: list):
        set_of_keys = set(keys) 

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
        self._quarantine_building = validators.ModelInstanceExistenceValidator.valid(
            model_cls=QuarantineBuilding,
            query_expr=Q(
                id=self._id,
            ),
            message=messages.QUARANTINE_BUILDING_NOT_FOUND,
        )
    
    def is_validate_name(self):
        if self.is_name_exist():
            raise exceptions.InvalidArgumentException(message={'name': messages.EXIST})

    def is_name_exist(self):
        try:
            quarantine_building = QuarantineBuilding.objects.get(id=self._id)
            quarantine_ward = quarantine_building.quarantine_ward
            old_name = quarantine_building.name
            if (old_name != self._name):
                name = validators.ModelInstanceExistenceValidator.valid(
                    model_cls=QuarantineBuilding,
                    query_expr=Q(
                        name=self._name,
                        quarantine_ward=quarantine_ward,
                    ),
                )
                return True
            return False
        except Exception as exception:
            return False
    
    def is_validate_is_full(self):
        value = self._is_full
        if value != None:
            self._is_full = validators.BooleanValidator.valid(
                value, 
                messages.INVALID_IS_FULL_FIELD,
            )
    
    def filter_validate(self):
        if hasattr(self, '_created_at_max'):
            validators.DateStringValidator.valid(self._created_at_max, message={'created_at_max': messages.INVALID})
            self._created_at_max = date_string_to_timestamp(self._created_at_max, 1)
        if hasattr(self, '_created_at_min'):
            validators.DateStringValidator.valid(self._created_at_min, message={'created_at_min': messages.INVALID})
            self._created_at_min = date_string_to_timestamp(self._created_at_min, 0)
        if hasattr(self, '_updated_at_max'):
            validators.DateStringValidator.valid(self._updated_at_max, message={'updated_at_max': messages.INVALID})
            self._updated_at_max = date_string_to_timestamp(self._updated_at_max, 1)
        if hasattr(self, '_updated_at_min'):
            validators.DateStringValidator.valid(self._updated_at_min, message={'updated_at_min': messages.INVALID})
            self._updated_at_min = date_string_to_timestamp(self._updated_at_min, 0)
        if hasattr(self, '_is_full'):
            self.is_validate_is_full()

