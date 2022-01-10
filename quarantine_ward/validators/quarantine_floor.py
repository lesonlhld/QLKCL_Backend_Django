from ..models import QuarantineBuilding, QuarantineFloor
from utils import validators, messages, exceptions
from django.db.models import Q
from utils.tools import date_string_to_timestamp

class QuarantineFloorValidator(validators.AbstractRequestValidate):

    def is_valid_fields(self, keys: list):
        set_of_keys = set(keys)

        return super().is_valid_fields(set_of_keys)

    def is_validate_quarantine_building(self):
        self._quarantine_building = validators.ModelInstanceExistenceValidator.valid(
            model_cls=QuarantineBuilding,
            query_expr=Q(
                id=self._quarantine_building,
            ),
            message=messages.QUARANTINE_BUILDING_NOT_FOUND,
        )
    
    def is_validate_id(self):
        self._id = validators.ModelInstanceExistenceValidator.valid(
            model_cls=QuarantineFloor,
            query_expr=Q(
                id=self._id,
            ),
            message=messages.QUARANTINE_FLOOR_NOT_FOUND,
        )
    
    def is_validate_is_full(self):
        value = self._is_full
        if value != None:
            self._is_full = validators.BooleanValidator.valid(
                value, 
                messages.INVALID_IS_FULL_FIELD,
            )
    
    def is_validate_room_quantity(self):
        value = self._room_quantity
        if value != None:
            self._room_quantity = validators.PositiveIntegerValidator.valid(
                self._room_quantity, message=messages.INVALID_ROOM_QUANTITY,
            )
    
    def is_validate_name(self):
        self.is_name_exist()

    def is_name_exist(self):
        try:
            name = validators.ModelInstanceExistenceValidator.valid(
                model_cls=QuarantineFloor,
                query_expr=Q(name=self._name),
                message={'name': messages.EXIST},
            )
            return True
        except Exception as exception:
            return False
    
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