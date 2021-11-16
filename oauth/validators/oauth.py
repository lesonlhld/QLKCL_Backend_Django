from django.db.models import Q
from user_account.models import CustomUser
from ..models import ResetPassword
from utils import validators, exceptions, messages
from utils.enums import ResetPasswordType
from django.utils import timezone

class OauthValidator(validators.AbstractRequestValidate):

    def is_valid_fields(self, keys: list):
        ignorable_fields = {'user'}
        set_of_keys = set(keys) - ignorable_fields

        return super().is_valid_fields(set_of_keys)

    def is_validate_email(self):
        if hasattr(self, '_email'):
            self._email = validators.EmailValidator.valid(self._email)
    
    def is_email_exist(self):
        if hasattr(self, '_email'):
            try:
                validators.ModelInstanceExistenceValidator.valid(
                    model_cls=CustomUser,
                    query_expr=Q(email=self._email),
                )
                return True
            except Exception as exception:
                return False
        return False
    
    def is_validate_otp(self):
        if hasattr(self, '_otp'):
            try:
                user = CustomUser.objects.get(email=self._email)
                validators.ModelInstanceExistenceValidator.valid(
                    model_cls=ResetPassword,
                    query_expr= Q(
                        otp=self._otp,
                        user=user,
                        type=ResetPasswordType.USER_INPUT,
                        created_at__gte=timezone.now()-timezone.timedelta(minutes=10),
                    )
                )
                return True
            except Exception as exception:
                raise exceptions.ValidationException(messages.INVALID_OTP)
        return False
    
    def is_validate_new_password(self):
        if hasattr(self, '_new_password'):
            value = self._new_password
            self._new_password = validators.PasswordValidator.valid(value)
            if hasattr(self, '_confirm_otp'):
                user = CustomUser.objects.get(email=self._email)
                if user.check_password(value):
                    raise exceptions.ValidationException(messages.DUPLICATE_NEW_PASSWORD)
            else:
                if (value == self._old_password):
                    raise exceptions.ValidationException(messages.DUPLICATE_NEW_PASSWORD)
            
    
    def is_validate_confirm_password(self):
        if hasattr(self, '_confirm_password'):
            value = self._confirm_password
            if value != self._new_password:
                raise exceptions.ValidationException(messages.CONFIRM_PASSWORD_NOT_MATCH)
    
    def is_validate_old_password(self):
        if hasattr(self, '_old_password'):
            value = self._old_password
            user = self._user
            if not user.check_password(value):
                raise exceptions.ValidationException(messages.WRONG_PASSWORD)
    
    def is_validate_confirm_otp(self):
        if hasattr(self, '_confirm_otp'):
            try:
                user = CustomUser.objects.get(email=self._email)
                validators.ModelInstanceExistenceValidator.valid(
                    model_cls=ResetPassword,
                    query_expr= Q(
                        otp=self._confirm_otp,
                        user=user,
                        type=ResetPasswordType.SYSTEM_HANDLE,
                        created_at__gte=timezone.now()-timezone.timedelta(minutes=10),
                    )
                )
                return True
            except Exception as exception:
                raise exceptions.ValidationException(messages.INVALID_OTP)
        return False
