from ..models import QuarantineFloor, QuarantineRoom
from user_account.models import Member
from utils import validators, messages, exceptions
from django.db.models import Q
from utils.tools import date_string_to_timestamp

class QuarantineRoomValidator(validators.AbstractRequestValidate):

    def is_valid_fields(self, keys: list):
        set_of_keys = set(keys) 

        return super().is_valid_fields(set_of_keys)

    def is_validate_quarantine_floor(self):
        self._quarantine_floor = validators.ModelInstanceExistenceValidator.valid(
            model_cls=QuarantineFloor,
            query_expr=Q(
                id=self._quarantine_floor,
            ),
            message=messages.QUARANTINE_FLOOR_NOT_FOUND,
        )

    def is_validate_capacity(self):
        value = self._capacity
        if value != None:
            self._capacity = validators.PositiveIntegerValidator.valid(
                self._capacity, message=messages.INVALID_CAPACITY_NUMBER,
            )
    
    def is_validate_id(self):
        quarantine_room = validators.ModelInstanceExistenceValidator.valid(
            model_cls=QuarantineRoom,
            query_expr=Q(
                id=self._id,
            ),
            message=messages.QUARANTINE_ROOM_NOT_FOUND,
        )
    
    def is_validate_is_full(self):
        value = self._is_full
        if value != None:
            self._is_full = validators.BooleanValidator.valid(
                value, 
                messages.INVALID_IS_FULL_FIELD,
            )
    
    def is_validate_name(self):
        if self.is_name_exist():
            raise exceptions.InvalidArgumentException(message={'name': messages.EXIST})

    def is_name_exist(self):
        try:
            quarantine_room = QuarantineRoom.objects.get(id=self._id)
            quarantine_floor = quarantine_room.quarantine_floor
            name = validators.ModelInstanceExistenceValidator.valid(
                model_cls=QuarantineRoom,
                query_expr=Q(
                    name=self._name,
                    quarantine_floor=quarantine_floor,
                ),
            )
            return True
        except Exception as exception:
            return False
    
    def check_capacity(self, quarantine_room):
        if hasattr(self, '_capacity'):
            num_current_member = Member.objects.filter(quarantine_room=quarantine_room).count()
            if (self._capacity < num_current_member):
                raise exceptions.InvalidArgumentException(message={'capacity': messages.UPDATED_CAPACITY_SMALLER_THAN_MEMBER})
    
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