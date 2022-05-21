from ..models import Notification, CustomUser
from utils import validators, messages, enums
from django.db.models import Q
from utils.tools import split_input_list

class NotificationValidator(validators.AbstractRequestValidate):

    def is_valid_fields(self, keys: list):
        ignorable_fields = {'title', 'description', 'url', 'page', 'page_size'}

        set_of_keys = set(keys) - ignorable_fields

        return super().is_valid_fields(set_of_keys)
    
    def is_validate_id(self):
        notification = validators.ModelInstanceExistenceValidator.valid(
            model_cls=Notification,
            query_expr=Q(
                id=self._id,
            ),
            message=messages.NOTIFICATION_NOT_FOUND,
        )

    def is_validate_image(self):
        if hasattr(self, '_image') and self._image:
            self._list_images = split_input_list(self._image)
    
    def is_validate_type(self):
        value = self._type
        if value != None:
            self._type = validators.EnumValidator.valid(
                value, 
                enums.NotificationType, 
                messages.INVALID_TYPE,
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
    
    def is_validate_user(self):
        self._user = validators.ModelInstanceExistenceValidator.valid(
            model_cls=CustomUser,
            query_expr=Q(
                id=self._user,
            ),
            message=messages.USER_NOT_FOUND,
        )

