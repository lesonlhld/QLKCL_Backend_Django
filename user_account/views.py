import os
import datetime
from random import randint
from django.views.decorators.csrf import csrf_exempt
from rest_framework import permissions
from rest_framework.decorators import action
from .validators.user import UserValidator
from .models import CustomUser, Member
from .serializers import CustomUserSerializer, MemberSerializer
from role.models import Role
from utils import exceptions, messages
from utils.enums import CustomUserStatus
from utils.views import AbstractView

# Create your views here.

class MemberAPI(AbstractView):

    permission_classes = [permissions.IsAuthenticated]

    def custom_user_code_generator(self, quarantine_ward_id):
        first_part_length = int(os.environ.get("USER_CODE_QUARANTINE_WARD_ID_LENGTH", "3"))
        first_part = ('0000000000' + str(quarantine_ward_id))[-first_part_length:]
        
        second_part_length = int(os.environ.get("USER_CODE_TIMESTAMP_LENGTH", "6"))
        second_part = ('0000000000' + str(int(datetime.datetime.now().timestamp())))[-second_part_length:]

        third_part_length = int(os.environ.get("USER_CODE_RANDOM_LENGTH", "6"))
        third_part = ''.join(str(randint(0, 9)) for i in range(third_part_length))

        return first_part + second_part + third_part

    @csrf_exempt
    @action(methods=['POST'], url_path='register', detail=False)
    def register_member(self, request):
        """For someone outside to register quarantine

        Args:
            + phone_number: String
            + password: String
            + quarantine_ward_id: int
        """

        accept_fields = [
            'phone_number', 'password',
            'quarantine_ward_id', 
        ]

        require_fields = [
            'phone_number', 'password',
            'quarantine_ward_id', 
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
                'phone_number', 'password',
            ])

            validator.extra_validate_to_register_member()

            # create CustomUser

            list_to_create_custom_user = ['phone_number', 'quarantine_ward']

            dict_to_create_custom_user = validator.get_data(list_to_create_custom_user)

            custom_user = CustomUser(**dict_to_create_custom_user)
            password = accepted_fields['password']
            custom_user.set_password(password)
            custom_user.code = self.custom_user_code_generator(custom_user.quarantine_ward.id)
            while (validator.is_code_exist(custom_user.code)):
                custom_user.code = self.custom_user_code_generator(custom_user.quarantine_ward.id)
            
            custom_user.created_by = request.user
            custom_user.updated_by = request.user
            custom_user.role = Role.objects.get(name='MEMBER')
            custom_user.status = CustomUserStatus.WAITING

            # create Member

            member = Member()
            member.custom_user = custom_user

            custom_user.save()
            member.save()

            custom_user_serializer = CustomUserSerializer(custom_user, many=False)
            member_serializer = MemberSerializer(member, many=False)
            
            response_data = dict()
            response_data['custom_user'] = custom_user_serializer.data
            response_data['member'] = member_serializer.data
            
            return self.response_handler.handle(data=response_data)
        except Exception as exception:
            return self.exception_handler.handle(exception)

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
            custom_user.code = self.custom_user_code_generator(custom_user.quarantine_ward.id)
            while (validator.is_code_exist(custom_user.code)):
                custom_user.code = self.custom_user_code_generator(custom_user.quarantine_ward.id)
            custom_user.created_by = request.user
            custom_user.updated_by = request.user
            custom_user.role = Role.objects.get(name='MEMBER')

            # create Member

            list_to_create_member = [key for key in accepted_fields.keys() if key in member_fields]
            list_to_create_member = set(list_to_create_member) - \
            {'quarantine_room_id'}
            list_to_create_member = list(list_to_create_member) + \
            ['quarantine_room']

            dict_to_create_member = validator.get_data(list_to_create_member)

            member = Member(**dict_to_create_member)
            member.custom_user = custom_user

            custom_user.save()
            member.save()

            custom_user_serializer = CustomUserSerializer(custom_user, many=False)
            member_serializer = MemberSerializer(member, many=False)
            
            response_data = dict()
            response_data['custom_user'] = custom_user_serializer.data
            response_data['member'] = member_serializer.data
            
            return self.response_handler.handle(data=response_data)
        except Exception as exception:
            return self.exception_handler.handle(exception)

    @csrf_exempt
    @action(methods=['POST'], url_path='get', detail=False)
    def get_user(self, request):
        """Get a user, if dont get id, will return user sending request

        Args:
            - code: int
        """

        accept_fields = [
            'code',
        ]

        try:
            request_extractor = self.request_handler.handle(request)
            receive_fields = request_extractor.data
            accepted_fields = dict()

            for key in receive_fields.keys():
                if key in accept_fields:
                    accepted_fields[key] = receive_fields[key]

            validator = UserValidator(**accepted_fields)

            custom_user = None

            if 'code' in accepted_fields.keys():
                if validator.is_code_exist():
                    custom_user = validator.get_field('custom_user')
                else:
                    raise exceptions.NotFoundException({'code': messages.NOT_EXIST})
            else:
                custom_user = request.user
            
            response_data = dict()

            custom_user_serializer = CustomUserSerializer(custom_user, many=False)

            response_data['custom_user'] = custom_user_serializer.data

            if hasattr(custom_user, 'member_x_custom_user') and custom_user.member_x_custom_user:
                member = custom_user.member_x_custom_user
                member_serializer = MemberSerializer(member, many=False)

                response_data['member'] = member_serializer.data
            
            return self.response_handler.handle(data=response_data)
        
        except Exception as exception:
            return self.exception_handler.handle(exception)

    @csrf_exempt
    @action(methods=['POST'], url_path='update', detail=False)
    def update_user(self, request):
        """Update a user, if dont get code, will update user sending request

        Args:
            - code: int
            - full_name: String
            - email: String
            - birthday: String 'dd/mm/yyyy'
            - gender: String [‘MALE’, ‘FEMALE’]
            - nationality_code: String
            - country_code: int
            - city_id: int
            - district_id: int
            - ward_id: int
            - detail_address: String
            - health_insurance_number: String
            - identity_number: String
            - passport_number: String
            - quarantine_ward_id: int
            - quarantine_room_id: int
            - label: String [‘F0’, ‘F1’, ‘F2’, ‘F3’]
            - quarantined_at: String 'dd/mm/yyyy'
            - positive_tested_before: boolean
            - background_disease: String '<id>,<id>,<id>'
            - other_background_disease: String
        """

        accept_fields = [
            'code', 'full_name', 'email',
            'birthday', 'gender', 'nationality_code',
            'country_code', 'city_id', 'district_id', 'ward_id',
            'detail_address', 'health_insurance_number',
            'identity_number', 'passport_number',
            'quarantine_ward_id', 'quarantine_room_id',
            'label', 'quarantined_at', 'positive_tested_before',
            'background_disease', 'other_background_disease',
        ]

        custom_user_fields = [
            'code', 'full_name', 'email',
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
            validator.is_valid_fields([
                'email', 'birthday', 'gender',
                'label', 'quarantined_at', 'positive_tested_before',
                'background_disease',
            ])
            validator.extra_validate_to_update_user()

            # update CustomUser

            custom_user = validator.get_field('custom_user')
            if not custom_user:
                custom_user = request.user

            list_to_update_custom_user = [key for key in accepted_fields.keys() if key in custom_user_fields]
            list_to_update_custom_user = set(list_to_update_custom_user) - \
            {'code', 'nationality_code', 'country_code', 'city_id', 'district_id', 'ward_id', 'quarantine_ward_id'}
            list_to_update_custom_user = list(list_to_update_custom_user) + \
            ['nationality', 'country', 'city', 'district', 'ward', 'quarantine_ward']
            dict_to_update_custom_user = validator.get_data(list_to_update_custom_user)

            for attr, value in dict_to_update_custom_user.items(): 
                setattr(custom_user, attr, value)

            custom_user.updated_by = request.user

            response_data = dict()
            custom_user_serializer = CustomUserSerializer(custom_user, many=False)
            response_data['custom_user'] = custom_user_serializer.data

            # update Member

            if hasattr(custom_user, 'member_x_custom_user') and custom_user.member_x_custom_user:
                member = custom_user.member_x_custom_user

                list_to_update_member = [key for key in accepted_fields.keys() if key in member_fields]
                list_to_update_member = set(list_to_update_member) - \
                {'quarantine_room_id'}
                list_to_update_member = list(list_to_update_member) + \
                ['quarantine_room']

                dict_to_update_member = validator.get_data(list_to_update_member)

                for attr, value in dict_to_update_member.items(): 
                    setattr(member, attr, value)

                member.save()

                member_serializer = MemberSerializer(member, many=False)
                response_data['member'] = member_serializer.data

            custom_user.save()

            return self.response_handler.handle(data=response_data)
        except Exception as exception:
            return self.exception_handler.handle(exception)

    @csrf_exempt
    @action(methods=['POST'], url_path='accept', detail=False)
    def accept_members(self, request):
        """Accept some members

        Args:
            + member_codes: String
        """

        accept_fields = [
            'member_codes',
        ]

        require_fields = [
            'member_codes',
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

            validator.extra_validate_to_accept_member()

            # accept members

            members = validator.get_field('members')

            for member in members:
                member.status = CustomUserStatus.AVAILABLE
                member.save()
            
            return self.response_handler.handle(data=messages.SUCCESS)
        except Exception as exception:
            return self.exception_handler.handle(exception)
