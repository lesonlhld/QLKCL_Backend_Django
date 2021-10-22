from datetime import datetime
from django.core.exceptions import (
    ValidationError,
    FieldError,
)
from django.http import JsonResponse
from django.shortcuts import render
from rest_framework import viewsets
from . import messages, exceptions

# Create your views here.

class JsonResponseHandler:

    @classmethod
    def handle(cls, data=None, error_code=0, message=messages.SUCCESS) -> JsonResponse:
        return JsonResponse(
            data={
                'data': data,
                'error_code': error_code,
                'message': message,
                "current_time": datetime.now(),
            }
        )

class ExceptionHandler:

    @classmethod
    def _get_code_and_message(cls, exception:Exception) -> set:
        print('=== type: ', type(exception), '=== ex: ', exception)

        default_message = (500, messages.CONTACT_ADMIN_FOR_SUPPORT)
        switcher = {
            exceptions.ValidationException: (400, str(exception)),
            exceptions.InvalidArgumentException: (400, exception.message) if hasattr(exception, 'message') else (400, str(exception)),
            exceptions.NotFoundException: (404, str(exception)),
            exceptions.AuthenticationException: (401, str(exception)),
            ValidationError: (400, messages.INVALID_ARGUMENT),
            ValueError: (400, str(exception)),
            FieldError: (400, messages.FIELD_NOT_SUPPORT),
            KeyError: (400, messages.FIELD_NOT_SUPPORT),
            exceptions.NetworkException: (500, str(exception)),
        }

        return switcher.get(type(exception), default_message)

    @classmethod
    def handle(cls, exception:Exception) -> JsonResponse:
        error_code, message = cls._get_code_and_message(exception)

        return JsonResponse(
            data={
                'data': None,
                'error_code': error_code,
                'message': message,
                "current_time": datetime.now(),
            }
        )

class RequestExtractor:

    def __init__(self, request):
        self.__request = request

        switch = {
            "POST": self.get_body_value,
            "GET": self.get_para_value,
        }

        self.get_value = switch[self.__request.method]

    def get_body_value(self, key, default=None):
        return self.__request.POST.get(key, default)

    def get_para_value(self, key, default=None):
        return self.__request.GET.get(key, default)

    @property
    def data(self):
        switch = {
            "POST": self.body,
            "GET": self.param,
        }
        return switch.get(self.__request.method, [])

    @property
    def body(self):
        return self.__request.POST.dict()

    @property
    def param(self):
        return self.__request.GET.dict()

class RequestHandler:

    @classmethod
    def handle(cls, request):
        return RequestExtractor(request)

class AbstractView(viewsets.GenericViewSet):

    response_handler = JsonResponseHandler
    exception_handler = ExceptionHandler
    request_handler = RequestHandler
