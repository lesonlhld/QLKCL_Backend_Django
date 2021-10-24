import re
from abc import ABC, abstractclassmethod
import datetime
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.db import models
from . import messages, exceptions

class AbstractValidator(ABC):
    @abstractclassmethod
    def valid(cls, value, message=messages.VALIDATION_EXCEPTION, *args, **kwargs):
        pass

class PhoneNumberValidator(AbstractValidator):
    PHONE_PATTERN = '^[+]{0,1}[0-9]{9,13}$'
    default_message = {'phone_number': messages.INVALID}

    @classmethod
    def valid(cls, value, message=default_message):
        if bool(re.match(cls.PHONE_PATTERN, value)):
            return value
        raise exceptions.ValidationException(message)

class EmailValidator(AbstractValidator):
    EMAIL_PATTERN = '^[a-zA-Z0-9](([.]{1}|[_]{1}|[-]{1}|[+]{1})?[a-zA-Z0-9])*[@]([a-z0-9]+([.]{1}|-)?)*[a-zA-Z0-9]+[.]{1}[a-z]{2,253}$'
    default_message = {'email': messages.INVALID}

    @classmethod
    def valid(cls, value, message=default_message):
        if bool(re.match(cls.EMAIL_PATTERN, value)):
            return value
        raise exceptions.ValidationException(message)

class DateStringValidator(AbstractValidator):
    DATE_PATTERN = '^[0-9]{2}/[0-9]{2}/[0-9]{4}$'
    default_message = {'date_string': messages.INVALID}

    @classmethod
    def valid(cls, value, message=default_message):
        if not bool(re.match(cls.DATE_PATTERN, value)):
            raise exceptions.ValidationException(message)
        try:
            datetime.datetime.strptime(value, '%d/%m/%Y')
            return value
        except Exception as exception:
            raise exceptions.ValidationException(message)

class EnumValidator(AbstractValidator):
    default_message = {'enum': messages.INVALID}

    @classmethod
    def valid(cls, value, enum_cls, message=default_message):
        value = value.upper()
        if value in [v.value for v in enum_cls.__members__.values()]:
            return value
        elif value in [k for k in enum_cls.__members__.keys()]:
            return str(enum_cls[value])
        raise exceptions.ValidationException(message)

class ModelInstanceExistenceValidator(AbstractValidator):
    default_message = {'object': messages.NOT_EXIST}

    @classmethod
    def valid(cls, model_cls, query_expr: models.Q, message=default_message):
        try:
            if isinstance(model_cls, models.query.QuerySet):  # check if a queryset is passed
                return model_cls.get(query_expr)
            else:
                return model_cls.objects.get(query_expr)

        except Exception as exception:
            raise exceptions.NotFoundException(message)

class BooleanValidator(AbstractValidator):
    default_message = {'boolean': messages.INVALID}

    @classmethod
    def valid(cls, value, message=default_message):
        if isinstance(value, str):
            if value.lower() in ("y", "yes", "t", "true", "1"):
                return True
            elif value.lower() in ("n", "no", "f", "false", "0"):
                return False
            else:
                raise exceptions.ValidationException(message)
        elif isinstance(value, int) and value in (0, 1):
            return bool(value)
        elif isinstance(value, bool):
            return value
        else:
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
            if self.has_field(key):
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
