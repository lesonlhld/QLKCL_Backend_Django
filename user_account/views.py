from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework import permissions
from rest_framework.decorators import action
from .validators.user import UserValidator
from .models import CustomUser, Member
from role.models import Role
from utils import exceptions, messages
from utils.views import AbstractView

# Create your views here.

class MemberAPI(AbstractView):

    permission_classes = [permissions.IsAuthenticated]

    @csrf_exempt
    @action(methods=['POST'], url_path='create', detail=False)
    def create_member(self, request):
        """Create a member

        Args:
            + full_name: String
            + phone_number: String
            - email: String
            + birthday: String 'dd/mm/yyyy'
            + gender: String [‘MALE’, ‘FEMALE’]
            + nationality_code: String
            + country_code: int
            + city_id: int
            + district_id: int
            + ward_id: int
            + detail_address: String
            - health_insurance_number: String
            - identity_number: String
            - passport_number: String
            + quarantine_ward_id: int
            - quarantine_room_id: int
            - label: String [‘F0’, ‘F1’, ‘F2’, ‘F3’]
            - quarantined_at: String 'dd/mm/yyyy'
            + positive_tested_before: boolean
            - background_disease: String '<id>,<id>,<id>'
            - other_background_disease: String
        """

        accept_fields = [
            'full_name', 'phone_number', 'email',
            'birthday', 'gender', 'nationality_code',
            'country_code', 'city_id', 'district_id', 'ward_id',
            'detail_address', 'health_insurance_number',
            'identity_number', 'passport_number',
            'quarantine_ward_id', 'quarantine_room_id',
            'label', 'quarantined_at', 'positive_tested_before',
            'background_disease', 'other_background_disease',
        ]

        require_fields = [
            'full_name', 'phone_number',
            'birthday', 'gender', 'nationality_code',
            'country_code', 'city_id', 'district_id', 'ward_id',
            'detail_address', 'quarantine_ward_id',
            'positive_tested_before',
        ]

        custom_user_fields = [
            'full_name', 'phone_number', 'email',
            'birthday', 'gender', 'nationality_code',
            'country_code', 'city_id', 'district_id', 'ward_id',
            'detail_address', 'health_insurance_number',
            'identity_number', 'passport_number',
            'quarantine_ward_id',
        ]

        member_fields = [
            'quarantine_room_id',
            'label', 'quarantined_at', 'positive_tested_before',
            'background_disease', 'other_background_disease',
        ]

        try:
            request_extractor = self.request_handler.handle(request)
            receive_fields = request_extractor.data
            accepted_fields = dict()

            for key in receive_fields.keys():
                if key in accept_fields:
                    accepted_fields[key] = receive_fields[key]

            validator = UserValidator(**accepted_fields)
            validator.is_missing_fields(require_fields)
            validator.is_valid_fields([
                'phone_number', 'email', 'birthday', 'gender',
                'label', 'quarantined_at', 'positive_tested_before',
                'background_disease',
            ])
            validator.extra_validate_to_create_member()

            # create CustomUser

            list_to_create_custom_user = [key for key in accepted_fields.keys() if key in custom_user_fields]
            list_to_create_custom_user = set(list_to_create_custom_user) - \
            {'nationality_code', 'country_code', 'city_id', 'district_id', 'ward_id', 'quarantine_ward_id'}
            list_to_create_custom_user = list(list_to_create_custom_user) + \
            ['nationality', 'country', 'city', 'district', 'ward', 'quarantine_ward']

            dict_to_create_custom_user = validator.get_data(list_to_create_custom_user)

            custom_user = CustomUser(**dict_to_create_custom_user)
            custom_user.set_password('123456')
            custom_user.created_by = request.user
            custom_user.updated_by = request.user
            custom_user.role = Role.objects.get(name='MEMBER')
            custom_user.save()

            # create Member

            list_to_create_member = [key for key in accepted_fields.keys() if key in member_fields]
            list_to_create_member = set(list_to_create_member) - \
            {'quarantine_room_id'}
            list_to_create_member = list(list_to_create_member) + \
            ['quarantine_room']

            dict_to_create_member = validator.get_data(list_to_create_member)

            member = Member(**dict_to_create_member)
            member.custom_user = custom_user
            member.save()
            
            return self.response_handler.handle(data='')
        except Exception as exception:
            return self.exception_handler.handle(exception)
