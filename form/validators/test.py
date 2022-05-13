from django.db.models import Q
from ..models import MedicalDeclaration, Test
from user_account.models import CustomUser
from quarantine_ward.models import QuarantineWard, QuarantineBuilding, QuarantineFloor, QuarantineRoom
from form.models import Symptom
from utils import validators, messages, exceptions
from utils.enums import TestStatus, TestType, TestResult
from utils.tools import split_input_list, date_string_to_timestamp

class TestValidator(validators.AbstractRequestValidate):

    def is_valid_fields(self, keys: list):
        ignorable_fields = {}
        set_of_keys = set(keys)

        return super().is_valid_fields(set_of_keys)

    def is_validate_status(self):
        if hasattr(self, '_status'):
            self._status = validators.EnumValidator.valid(
                value=self._status,
                enum_cls=TestStatus,
                message={'status': messages.INVALID},
            )

    def is_validate_type(self):
        if hasattr(self, '_type'):
            self._type = validators.EnumValidator.valid(
                value=self._type,
                enum_cls=TestType,
                message={'type': messages.INVALID},
            )

    def is_validate_result(self):
        if hasattr(self, '_result'):
            self._result = validators.EnumValidator.valid(
                value=self._result,
                enum_cls=TestResult,
                message={'result': messages.INVALID},
            )

    def is_validate_created_at_max(self):
        if hasattr(self, '_created_at_max'):
            self._created_at_max = validators.DateTimeFieldValidator.valid(
                value=self._created_at_max,
                message={'created_at_max': messages.INVALID_DATETIME},
            )

    def is_validate_created_at_min(self):
        if hasattr(self, '_created_at_min'):
            self._created_at_min = validators.DateTimeFieldValidator.valid(
                value=self._created_at_min,
                message={'created_at_min': messages.INVALID_DATETIME},
            )

    def is_validate_updated_at_max(self):
        if hasattr(self, '_updated_at_max'):
            self._updated_at_max = validators.DateTimeFieldValidator.valid(
                value=self._updated_at_max,
                message={'updated_at_max': messages.INVALID_DATETIME},
            )

    def is_validate_updated_at_min(self):
        if hasattr(self, '_updated_at_min'):
            self._updated_at_min = validators.DateTimeFieldValidator.valid(
                value=self._updated_at_min,
                message={'updated_at_min': messages.INVALID_DATETIME},
            )

    def is_code_exist(self, code=None):
        if code:
            try:
                validators.ModelInstanceExistenceValidator.valid(
                    model_cls=Test,
                    query_expr=Q(code=code),
                )
                return True
            except Exception as exception:
                return False
        else:
            if hasattr(self, '_code'):
                try:
                    self._test = validators.ModelInstanceExistenceValidator.valid(
                        model_cls=Test,
                        query_expr=Q(code=self._code),
                    )
                    return True
                except Exception as exception:
                    return False
            return False

    def is_phone_number_exist(self):
        if hasattr(self, '_phone_number'):
            try:
                self._user = validators.ModelInstanceExistenceValidator.valid(
                    model_cls=CustomUser,
                    query_expr=Q(phone_number=self._phone_number),
                )
                return True
            except Exception as exception:
                return False
        return False

    def is_user_code_exist(self):
        if hasattr(self, '_user_code'):
            try:
                self._user = validators.ModelInstanceExistenceValidator.valid(
                    model_cls=CustomUser,
                    query_expr=Q(code=self._user_code),
                )
                return True
            except Exception as exception:
                return False
        return False

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
        return True

    def is_quarantine_building_id_exist(self):
        if hasattr(self, '_quarantine_building_id'):
            try:
                self._quarantine_building = validators.ModelInstanceExistenceValidator.valid(
                    model_cls=QuarantineBuilding,
                    query_expr=Q(id=self._quarantine_building_id),
                )
                return True
            except Exception as exception:
                return False
        return True

    def is_quarantine_floor_id_exist(self, id=None):
        if id:
            try:
                validators.ModelInstanceExistenceValidator.valid(
                    model_cls=QuarantineFloor,
                    query_expr=Q(id=id),
                )
                return True
            except Exception as exception:
                return False
        elif hasattr(self, '_quarantine_floor_id'):
            try:
                self._quarantine_floor = validators.ModelInstanceExistenceValidator.valid(
                    model_cls=QuarantineFloor,
                    query_expr=Q(id=self._quarantine_floor_id),
                )
                return True
            except Exception as exception:
                return False
        return True

    def is_quarantine_room_id_exist(self):
        if hasattr(self, '_quarantine_room_id'):
            try:
                self._quarantine_room = validators.ModelInstanceExistenceValidator.valid(
                    model_cls=QuarantineRoom,
                    query_expr=Q(id=self._quarantine_room_id),
                )
                return True
            except Exception as exception:
                return False
        return True

    def get_user_by_code(self, code):
        try:
            user = validators.ModelInstanceExistenceValidator.valid(
                model_cls=CustomUser,
                query_expr=Q(code=code),
            )
            return user
        except Exception as exception:
            return None

    def check_quarantine_ward_room_relationship(self):
        if hasattr(self, '_quarantine_room'):
            if not hasattr(self, '_quarantine_floor'):
                self._quarantine_floor = self._quarantine_room.quarantine_floor
                self._quarantine_floor_id = self._quarantine_room.quarantine_floor.id
            else:
                if self._quarantine_floor != self._quarantine_room.quarantine_floor:
                    raise exceptions.ValidationException({'quarantine_ward_room_relationship': messages.INVALID})
        
        if hasattr(self, '_quarantine_floor'):
            if not hasattr(self, '_quarantine_building'):
                self._quarantine_building = self._quarantine_floor.quarantine_building
                self._quarantine_building_id = self._quarantine_floor.quarantine_building.id
            else:
                if self._quarantine_building != self._quarantine_floor.quarantine_building:
                    raise exceptions.ValidationException({'quarantine_ward_room_relationship': messages.INVALID})

        if hasattr(self, '_quarantine_building'):
            if not hasattr(self, '_quarantine_ward'):
                self._quarantine_ward = self._quarantine_building.quarantine_ward
                self._quarantine_ward_id = self._quarantine_building.quarantine_ward.id
            else:
                if self._quarantine_ward != self._quarantine_building.quarantine_ward:
                    raise exceptions.ValidationException({'quarantine_ward_room_relationship': messages.INVALID})

    def extra_validate_to_create_test(self):
        if hasattr(self, '_phone_number') and not self.is_phone_number_exist():
            raise exceptions.ValidationException({'phone_number': messages.NOT_EXIST})
        if hasattr(self, '_result'):
            if self._result in [TestResult.POSITIVE, TestResult.NEGATIVE]:
                self._status = TestStatus.DONE
            else:
                self._status = TestStatus.WAITING

    def extra_validate_to_create_many_test(self):
        if hasattr(self, '_user_codes'):
            self._user_codes = split_input_list(self._user_codes)
            self._users = []
            for code in self._user_codes:
                user = self.get_user_by_code(code)
                if not user:
                    raise exceptions.NotFoundException({'main': f'{code}: ' + messages.NOT_EXIST})
                self._users += [user]

    def extra_validate_to_get_test(self):
        if hasattr(self, '_code') and not self.is_code_exist():
            raise exceptions.ValidationException({'main': messages.TEST_NOT_FOUND})

    def extra_validate_to_update_test(self):
        if hasattr(self, '_code') and not self.is_code_exist():
            raise exceptions.ValidationException({'main': messages.TEST_NOT_FOUND})

        if hasattr(self, '_result'):
            if self._result in [TestResult.POSITIVE, TestResult.NEGATIVE]:
                self._status = TestStatus.DONE
            else:
                self._status = TestStatus.WAITING
            
    def extra_validate_to_filter_test(self):
        if hasattr(self, '_user_code') and not self.is_user_code_exist():
            raise exceptions.ValidationException({'main': messages.USER_NOT_FOUND})
        if hasattr(self, '_quarantine_ward_id') and not self.is_quarantine_ward_id_exist():
            raise exceptions.NotFoundException({'quarantine_ward_id': messages.NOT_EXIST})
        if hasattr(self, '_quarantine_building_id') and not self.is_quarantine_building_id_exist():
            raise exceptions.NotFoundException({'quarantine_building_id': messages.NOT_EXIST})
        if hasattr(self, '_quarantine_floor_id') and not self.is_quarantine_floor_id_exist():
            raise exceptions.NotFoundException({'quarantine_floor_id': messages.NOT_EXIST})
        if hasattr(self, '_quarantine_room_id') and not self.is_quarantine_room_id_exist():
            raise exceptions.NotFoundException({'quarantine_room_id': messages.NOT_EXIST})
        self.check_quarantine_ward_room_relationship()
        