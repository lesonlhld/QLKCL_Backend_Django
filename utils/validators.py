import re
from abc import ABC, abstractclassmethod
from . import messages, exceptions

class AbstractValidator(ABC):
    @abstractclassmethod
    def valid(cls, value, message=messages.VALIDATION_EXCEPTION, *args, **kwargs):
        pass

class PhoneNumberValidator(AbstractValidator):
    PHONE_PATTERN = '^[+]{0,1}[0-9]{5,13}$'

    @classmethod
    def valid(cls, value, message=messages.INVALID_PHONE_NUMBER):
        if bool(re.match(cls.PHONE_PATTERN, value)):
            return value
        raise exceptions.ValidationException(message)

class PositiveFloatValidator(AbstractValidator):

    @classmethod
    def valid(cls, value, message=messages.INVALID_POSITIVE_FLOAT):
        try:
            value = float(value)
        except Exception as exception:
            raise exceptions.ValidationException(message)

        if value <= 0:
            raise exceptions.ValidationException(message)

        return value

class AbstractRequestValidate(ABC):
    def __init__(self, *args, **kwargs):
        for key, value in kwargs.items():
            setattr(self, f'_{key}', value)

    def is_missing_fields(self, keys: list):
        """Check if value of keys is empty

        Args:
            keys (list): list of keys

        Raises:
            exceptions.ApplicationException: when field not exist in objest
            exceptions.InvalidArgumentException: missing there fields
        """

        errors = dict()
        for key in keys:
            label = f'_{key}'
            if not hasattr(self, label) or not getattr(self, label):
                errors[f'{key}'] = 'empty'
        if errors:
            raise exceptions.InvalidArgumentException(message=errors)

    def is_valid_fields(self, keys: list):
        """Validate value of keys by calling method validate_{key}.
        If value is None, don't do anything.

        Args:
            keys (list): a list of keys
        """
        for key in keys:
            label = f'_{key}'
            if hasattr(self, label):
                if hasattr(self, f'is_validate{label}'):
                    getattr(self, f'is_validate{label}')()
                else:
                    raise exceptions.ValidationException(
                        f'Not support field: {key}'
                    )

    def get_data(self, keys):
        result = dict()
        for key in keys:
            result[key] = self.get_field(key)
        return result

    def has_field(self, key: str):
        label = f'_{key}'
        return hasattr(self, label)

    def has_fields(self, keys):
        for key in keys:
            if not self.has_field(key):
                return False
        return True

    def get_field(self, key: str):
        label = f'_{key}'
        return getattr(self, label, None)
