from ..models import UserNotification, Notification, CustomUser
from quarantine_ward.models import QuarantineWard
from utils import validators, messages, enums, exceptions
from django.db.models import Q
from utils.tools import split_input_list

class UserNotificationValidator(validators.AbstractRequestValidate):

    def is_valid_fields(self, keys: list):

        ignorabled_fields = {'page', 'page_size'}
        
        set_of_keys = set(keys) - ignorabled_fields

        return super().is_valid_fields(set_of_keys)
    
    def is_validate_user(self):
        self._user = validators.ModelInstanceExistenceValidator.valid(
            model_cls=CustomUser,
            query_expr=Q(
                id=self._user,
            ),
            message=messages.USER_NOT_FOUND,
        )
        return self._user
    
    def is_validate_notification(self):
        self._notification = validators.ModelInstanceExistenceValidator.valid(
            model_cls=Notification,
            query_expr=Q(
                id=self._notification,
            ),
            message=messages.NOTIFICATION_NOT_FOUND,
        )
        return self._notification

    def is_user_notification_exist(self):
        user_notification = validators.ModelInstanceExistenceValidator.valid(
            model_cls=UserNotification,
            query_expr=Q(
                user__id=self._user.id,
                notification__id=self._notification.id,
            ),
            message=messages.USER_NOTIFICATION_NOT_FOUND,
        )
        return user_notification
    
    def is_user_notification_exist_with_args(self, user, notification):
        if self._is_user_notification_exist_with_args(user, notification):
            raise exceptions.InvalidArgumentException({f'UserNotification with user {user.id} and notification {notification.id}': messages.EXIST})

    def _is_user_notification_exist_with_args(self, user, notification):
        try:
            user_notification = validators.ModelInstanceExistenceValidator.valid(
                model_cls=UserNotification,
                query_expr=Q(
                    user__id=user.id,
                    notification__id=notification.id,
                ),
            )
            return True
        except Exception as exception:
            return False

    def is_user_notification_exist_with_args_list(self, user, list_notification):
        user_notification_id_list = []
        for notification in list_notification:
            try:
                user_notification = validators.ModelInstanceExistenceValidator.valid(
                    model_cls=UserNotification,
                    query_expr=Q(
                        user__id=user.id,
                        notification__id=notification.id,
                    ),
                )
                user_notification_id_list += [user_notification.id]
            except Exception as exception:
                print(exception)
                raise exceptions.NotFoundException({f'UserNotification with user {user.id} and notification {notification.id}': messages.NOT_EXIST})
        return user_notification_id_list
    
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
        for user_code in user_list:
            try:
                user = validators.ModelInstanceExistenceValidator.valid(
                    model_cls=CustomUser,
                    query_expr=Q(code=user_code),
                )
                user_code_list += [user.code]
            except Exception as exception:
                raise exceptions.NotFoundException({f'User {user_code}': messages.NOT_EXIST})
        return user_code_list
    
    def is_validate_notification_list(self):
        notification_id_list = split_input_list(self._notification_list)
        notification_list = []
        for id in notification_id_list:
            try:
                notification = validators.ModelInstanceExistenceValidator.valid(
                    model_cls=Notification,
                    query_expr=Q(id=id),
                )
                notification_list += [notification]
            except Exception as exception:
                raise exceptions.NotFoundException({f'Notification (id = {id})': messages.NOT_EXIST})
        return notification_list
    
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
