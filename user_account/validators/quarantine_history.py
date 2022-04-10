from django.db.models import Q
from ..models import CustomUser, QuarantineHistory
from utils import validators, messages, exceptions

class QuarantineHistoryValidator(validators.AbstractRequestValidate):

    def is_valid_fields(self, keys: list):
        ignorable_fields = {}
        set_of_keys = set(keys)

        return super().is_valid_fields(set_of_keys)

    def is_id_exist(self):
        if hasattr(self, '_id'):
            try:
                self._quarantine_history = validators.ModelInstanceExistenceValidator.valid(
                    model_cls=QuarantineHistory,
                    query_expr=Q(id=self._id),
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

    def extra_validate_to_get_quarantine_history(self):
        if hasattr(self, '_id') and not self.is_id_exist():
            raise exceptions.NotFoundException({'id': messages.NOT_EXIST})

    def extra_validate_to_filter_quarantine_history(self):
        if hasattr(self, '_user_code') and not self.is_user_code_exist():
            raise exceptions.NotFoundException({'user_code': messages.NOT_EXIST})

    def extra_validate_to_fix_empty_quarantine_history(self):
        if hasattr(self, '_user_code') and not self.is_user_code_exist():
            raise exceptions.NotFoundException({'user_code': messages.NOT_EXIST})
        if hasattr(self, '_user'):
            if self._user.role.name != 'MEMBER' or not hasattr(self._user, 'member_x_custom_user'):
                raise exceptions.ValidationException({'user_code': messages.ISNOTMEMBER})