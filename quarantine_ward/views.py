from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import action
from utils.views import AbstractView
from utils import exceptions, messages
from .models import QuarantineWard
from .validators.quarantine_ward import QuarantineWardValidator
# Create your views here.

class QuarantineWardAPI (AbstractView):
    
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

            validator = QuarantineWardValidator(**accepted_fields)
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
    def create_quarantineward(self, request):
        """Create a Quarantine Ward

        Args:
            + email (str)
            + full_name (str)
            + country (str): country_code
            + city (str): city_code
            + district (str): district_code
            + ward (str): ward_code
            - address (str)
            - latitude (str)
            - longitude (str)
            - status (str)
            - type (str)
            - quarantine_time (int)
            + main_manager (str): id
        """

        accept_fields = [
            'email', 'full_name', 'country', 'city',
            'district', 'ward', 'address', 'latitude',
            'longitude', 'status', 'type', 'quarantine_time',
            'main_manager',
        ]

        require_fields = [
            'email', 'full_name', 'country', 'city',
            'district', 'ward','main_manager',
        ]

        try:
            request_extractor = self.request_handler.handle(request)
            receive_fields = request_extractor.data
            accepted_fields = dict()

            for key in receive_fields:
                if key in accept_fields:
                    accepted_fields[key] = receive_fields[key]

            validator = QuarantineWardValidator(**accepted_fields)
            validator.is_missing_fields(require_fields)

            list_to_create_country = accepted_fields.keys()
            dict_to_create_country = validator.get_data(list_to_create_country)
            quarantine_ward = QuarantineWard(**dict_to_create_country)
            quarantine_ward.save()

            serializer = QuarantineWardSerializer(quarantine_ward, many=False)
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