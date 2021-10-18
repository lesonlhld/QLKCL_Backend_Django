from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import action
from .models import Country
from .serializers import CountrySerializer, CitySerializer, DistrictSerializer, WardSerializer
from .validators.country import CountryValidator
from utils import exceptions, messages
from utils.views import AbstractView

# Create your views here.

class CountryAPI(AbstractView):

    @csrf_exempt
    @action(methods=['GET'], url_path='get', detail=False)
    def get_country(self, request):
        """Get a Country

        Args:
            + code (str)
        """

        accept_fields = [
            'code',
        ]

        require_fields = [
            'code',
        ]

        try:
            request_extractor = self.request_handler.handle(request)
            receive_fields = request_extractor.data
            accepted_fields = dict()

            for key in receive_fields:
                if key in accept_fields:
                    accepted_fields[key] = receive_fields[key]

            validator = CountryValidator(**accepted_fields)
            validator.is_missing_fields(require_fields)
            
            if not validator.is_code_exist():
                raise exceptions.InvalidArgumentException({'code': messages.NOT_EXIST})

            country = validator.get_field('country')

            serializer = CountrySerializer(country, many=False)
            return self.response_handler.handle(data=serializer.data)
        except Exception as exception:
            return self.exception_handler.handle(exception)

    @csrf_exempt
    @action(methods=['POST'], url_path='create', detail=False)
    def create_country(self, request):
        """Create a Country

        Args:
            + code (str)
            + name (str)
        """

        accept_fields = [
            'code', 'name',
        ]

        require_fields = [
            'code', 'name',
        ]

        try:
            request_extractor = self.request_handler.handle(request)
            receive_fields = request_extractor.data
            accepted_fields = dict()

            for key in receive_fields:
                if key in accept_fields:
                    accepted_fields[key] = receive_fields[key]

            validator = CountryValidator(**accepted_fields)
            validator.is_missing_fields(require_fields)
            if validator.is_code_exist():
                raise exceptions.InvalidArgumentException({'code': messages.EXIST})

            list_to_create_country = accepted_fields.keys()
            dict_to_create_country = validator.get_data(list_to_create_country)
            country = Country(**dict_to_create_country)
            country.save()

            serializer = CountrySerializer(country, many=False)
            return self.response_handler.handle(data=serializer.data)
        except Exception as exception:
            return self.exception_handler.handle(exception)

    @csrf_exempt
    @action(methods=['POST'], url_path='update', detail=False)
    def update_country(self, request):
        """Update a Country

        Args:
            + code (str)
            - name (str)
        """

        accept_fields = [
            'code', 'name',
        ]

        require_fields = [
            'code',
        ]

        try:
            request_extractor = self.request_handler.handle(request)
            receive_fields = request_extractor.data
            accepted_fields = dict()

            for key in receive_fields:
                if key in accept_fields:
                    accepted_fields[key] = receive_fields[key]

            validator = CountryValidator(**accepted_fields)
            validator.is_missing_fields(require_fields)

            if not validator.is_code_exist():
                raise exceptions.InvalidArgumentException({'code': messages.NOT_EXIST})

            country = validator.get_field('country')

            list_to_update_country = accepted_fields.keys() - {'code'}

            dict_to_update_country = validator.get_data(list_to_update_country)

            country.__dict__.update(**dict_to_update_country)

            country.save()

            serializer = CountrySerializer(country, many=False)
            return self.response_handler.handle(data=serializer.data)
        except Exception as exception:
            return self.exception_handler.handle(exception)

    @csrf_exempt
    @action(methods=['POST'], url_path='delete', detail=False)
    def delete_country(self, request):
        """Delete a Country

        Args:
            + code (str)
        """

        accept_fields = [
            'code',
        ]

        require_fields = [
            'code',
        ]

        try:
            request_extractor = self.request_handler.handle(request)
            receive_fields = request_extractor.data
            accepted_fields = dict()

            for key in receive_fields:
                if key in accept_fields:
                    accepted_fields[key] = receive_fields[key]

            validator = CountryValidator(**accepted_fields)
            validator.is_missing_fields(require_fields)

            if not validator.is_code_exist():
                raise exceptions.InvalidArgumentException({'code': messages.NOT_EXIST})

            country = validator.get_field('country')

            country.delete()

            serializer = CountrySerializer(country, many=False)
            return self.response_handler.handle(data=serializer.data)
        except Exception as exception:
            return self.exception_handler.handle(exception)

    @csrf_exempt
    @action(methods=['POST'], url_path='filter', detail=False)
    def filter_country(self, request):
        """List all Country

        Args:
            None
        """

        try:
            list_country = Country.objects.all()

            serializer = CountrySerializer(list_country, many=True)
            return self.response_handler.handle(data=serializer.data)
        except Exception as exception:
            return self.exception_handler.handle(exception)
