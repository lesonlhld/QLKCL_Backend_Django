import imp
import os
import functools
import time
import json
from datetime import datetime
from django.core.exceptions import (
    ValidationError,
    FieldError,
)
from django.db import connection, reset_queries
from django.http import JsonResponse
from django.shortcuts import render
from django.core.paginator import Paginator
from rest_framework import viewsets, serializers
from . import messages, exceptions

# Create your views here.

def paginate_data(request, data):
    """
    Function to handle pagination data.

    Params:

    data: array data.

    request: request object that contain paginate info

    page: page to show (Default is 1).

    page_size: Defaults is 10 (PAGE_SIZE=10).

    Return a JSON data:

    response_data = {
        "totalRows": total,
        "totalPages": total_pages,
        "currentPage": page_number,
        "content": content
    }
    """

    PAGE_SIZE = int(os.environ.get("PAGE_SIZE"))
    PAGE_SIZE_MAX = int(os.environ.get("PAGE_SIZE_MAX"))

    try:
        page = int(request.data.get("page", 1))
    except Exception as exception:
        raise ValueError(messages.NEGATIVE_PAGE)

    try:
        page_size = int(request.data.get("page_size", PAGE_SIZE))
    except Exception as exception:
        raise ValueError(messages.NEGATIVE_PAGE_SIZE)

    # Handle page_size = 'all'
    # page_size = 0 for get all
    if page_size == 0:
        page_size = len(data) + 1
    elif page_size < 0:
        raise ValueError(messages.NEGATIVE_PAGE_SIZE)
    elif page_size > PAGE_SIZE_MAX:
        raise ValueError(messages.OVER_PAGE_SIZE_MAX + str(PAGE_SIZE_MAX))

    if page <= 0:
        raise ValueError(messages.NEGATIVE_PAGE)

    paginator = Paginator(data, page_size)

    total_pages = paginator.num_pages

    if int(total_pages) < page:
        page_number = page
        content = []
    else:
        current_page = paginator.page(page)
        page_number = current_page.number
        content = current_page.object_list

    total = paginator.count

    response_data = {
        "totalRows": total,
        "totalPages": total_pages,
        "currentPage": page_number,
        "content": content,
        "pageSize": page_size,
    }

    return response_data

# Calculate query time and number of query statement
def query_debugger(func):
    @functools.wraps(func)
    def inner_func(*args, **kwargs):
        reset_queries()

        start_queries = len(connection.queries)

        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()

        end_queries = len(connection.queries)

        result_dict = json.loads(result.content)
        result_dict['Number of Queries'] = end_queries - start_queries
        result_dict['Finished in'] = end - start
        
        return JsonResponse(
            data=result_dict,
        )

    return inner_func

class EmptySerializer(serializers.Serializer):
    pass

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
            exceptions.ValidationException: (400, exception.message) if hasattr(exception, 'message') else (400, str(exception)),
            exceptions.InvalidArgumentException: (400, exception.message) if hasattr(exception, 'message') else (400, str(exception)),
            exceptions.NotFoundException: (400, exception.message) if hasattr(exception, 'message') else (400, str(exception)),
            exceptions.AuthenticationException: (401, exception.message) if hasattr(exception, 'message') else (401, str(exception)),
            ValidationError: (400, messages.INVALID_ARGUMENT),
            ValueError: (400, exception.message) if hasattr(exception, 'message') else (400, str(exception)),
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

    serializer_class = EmptySerializer
    response_handler = JsonResponseHandler
    exception_handler = ExceptionHandler
    request_handler = RequestHandler
    swagger_fake_view = True
