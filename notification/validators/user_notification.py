from ..models import UserNotification, Notification, CustomUser
from quarantine_ward.models import QuarantineWard
from utils import validators, messages, enums, exceptions
from django.db.models import Q
from utils.tools import split_input_list

class UserNotificationValidator(validators.AbstractRequestValidate):

    def is_valid_fields(self, keys: list):

        set_of_keys = set(keys)

        return super().is_valid_fields(set_of_keys)
    
    def is_validate_user(self):
        self._user = validators.ModelInstanceExistenceValidator.valid(
            model_cls=CustomUser,
            query_expr=Q(
                id=self._user,
            ),
            message=messages.USER_NOT_FOUND,
        )
    
    def is_validate_notification(self):
        self._notification = validators.ModelInstanceExistenceValidator.valid(
            model_cls=Notification,
            query_expr=Q(
                id=self._notification,
            ),
            message=messages.NOTIFICATION_NOT_FOUND,
        )
        return self._notification

    def is_user_notification_exist(self, user):
        user_notification = validators.ModelInstanceExistenceValidator.valid(
            model_cls=UserNotification,
            query_expr=Q(
                user=user,
                notification=self._notification
            ),
            message=messages.USER_NOTIFICATION_NOT_FOUND,
        )
        return user_notification
    
    def is_validate_type(self):
        value = int(self._type)
        if value not in range(0, 3):
            raise exceptions.ValidationException(message=messages.INVALID_TYPE)
        return value
    
    def is_validate_role(self):
        value = int(self._role)
        if value not in range(0, 6):
            raise exceptions.ValidationException(message=messages.INVALID_ROLE_ID)
        return value

    def is_validate_quarantine_ward(self):
        self._quarantine_ward = validators.ModelInstanceExistenceValidator.valid(
            model_cls=QuarantineWard,
            query_expr=Q(
                id=self._quarantine_ward,
            ),
            message=messages.QUARANTINE_WARD_NOT_FOUND,
        )
        return self._quarantine_ward
    
    def is_validate_user_list(self):
        user_list = split_input_list(self._users)
        user_code_list = []
        for user_id in user_list:
            try:
                user = validators.ModelInstanceExistenceValidator.valid(
                    model_cls=CustomUser,
                    query_expr=Q(id=user_id),
                )
                user_code_list += [user.code]
            except Exception as exception:
                raise exceptions.NotFoundException({f'User {user_id}': messages.NOT_EXIST})
    
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
