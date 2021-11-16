import os
import datetime
from random import randint
from django.views.decorators.csrf import csrf_exempt
from rest_framework import permissions
from rest_framework.decorators import action, permission_classes
from .validators.user import UserValidator
from .models import CustomUser, Member
from .serializers import CustomUserSerializer, MemberSerializer, FilterMemberSerializer, FilterNotMemberSerializer
from .filters.user import UserFilter
from form.models import Test
from form.filters.test import TestFilter
from role.models import Role
from utils import exceptions, messages
from utils.enums import CustomUserStatus, HealthStatus, TestStatus
from utils.views import AbstractView, paginate_data
from utils.tools import date_string_to_timestamp, timestamp_string_to_date_string

# Create your views here.

class MemberAPI(AbstractView):

    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.action == 'register_member':
            self.permission_classes = [permissions.AllowAny]
        return super().get_permissions()

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
            - positive_tested_before: boolean
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
                'passport_number', 'health_insurance_number', 'identity_number',
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
            member.quarantined_at = timestamp_string_to_date_string(datetime.datetime.now())

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
                'email', 'birthday', 'gender', 'passport_number',
                'health_insurance_number', 'identity_number',
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
            + member_codes: String <code>,<code>
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

            custom_users = validator.get_field('members')

            for custom_user in custom_users:
                custom_user.status = CustomUserStatus.AVAILABLE
                if hasattr(custom_user, 'member_x_custom_user'):
                    member = custom_user.member_x_custom_user
                    member.quarantined_at = timestamp_string_to_date_string(datetime.datetime.now())
                    member.save()
                custom_user.created_by = request.user
                custom_user.updated_by = request.user
                custom_user.save()
            
            return self.response_handler.handle(data=messages.SUCCESS)
        except Exception as exception:
            return self.exception_handler.handle(exception)

    @csrf_exempt
    @action(methods=['POST'], url_path='refuse', detail=False)
    def refuse_members(self, request):
        """Refuse some members

        Args:
            + member_codes: String <code>,<code>
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

            validator.extra_validate_to_refuse_member()

            # refuse members

            custom_users = validator.get_field('members')

            for custom_user in custom_users:
                custom_user.status = CustomUserStatus.REFUSED
                custom_user.created_by = request.user
                custom_user.updated_by = request.user
                custom_user.save()

            return self.response_handler.handle(data=messages.SUCCESS)
        except Exception as exception:
            return self.exception_handler.handle(exception)

    @csrf_exempt
    @action(methods=['POST'], url_path='filter', detail=False)
    def filter_member(self, request):
        """Get a list of members

        Args:
            - status: String ['WAITING', 'REFUSED', 'LOCKED', 'AVAILABLE']
            - health_status_list: String <status>,<status> ['NORMAL', 'UNWELL', 'SERIOUS']
            - positive_test: boolean
            - is_last_tested: boolean - True để lọc những người cách ly đến hạn xét nghiệm, False hoặc không truyền đồng nghĩa không lọc
            - can_finish_quarantine: boolean - True để lọc những người cách ly có thể hoàn thành cách ly, False hoặc không truyền đồng nghĩa không lọc
            - created_at_max: String 'dd/mm/yyyy'
            - created_at_min: String 'dd/mm/yyyy'
            - quarantined_at_max: String 'dd/mm/yyyy'
            - quarantined_at_min: String 'dd/mm/yyyy'
            - quarantine_ward_id: String
            - quarantine_building_id: String
            - quarantine_floor_id: String
            - quarantine_room_id: String
            - abroad: boolean - True để lọc những người cách ly nhập cảnh, False để lọc những người không nhập cảnh, không truyền để không lọc
            - label: String ['F0', 'F1', 'F2', 'F3']
            - page: int
            - page_size: int
            - search: String
        """

        accept_fields = [
            'status', 'health_status_list', 'positive_test',
            'is_last_tested', 'can_finish_quarantine',
            'created_at_max', 'created_at_min',
            'quarantined_at_max', 'quarantined_at_min',
            'quarantine_ward_id', 'quarantine_building_id',
            'quarantine_floor_id', 'quarantine_room_id',
            'label', 'abroad',
            'page', 'page_size', 'search',
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
                'status', 'positive_test', 'health_status_list', 'is_last_tested',
                'can_finish_quarantine', 'created_at_max', 'created_at_min',
                'quarantined_at_max', 'quarantined_at_min', 'label', 'abroad',
            ])
            validator.extra_validate_to_filter_member()

            query_set = CustomUser.objects.all()

            list_to_filter_user = [key for key in accepted_fields.keys()]
            list_to_filter_user = set(list_to_filter_user) - \
            {'is_last_tested', 'page', 'page_size'}
            list_to_filter_user = list(list_to_filter_user) + \
            [
                'last_tested_max', 'role_name', 'quarantined_at_max',
                'positive_test', 'health_status_list',
            ]

            dict_to_filter_user = validator.get_data(list_to_filter_user)

            dict_to_filter_user.setdefault('order_by', '-created_at')

            filter = UserFilter(dict_to_filter_user, queryset=query_set)

            query_set = filter.qs

            query_set = query_set.select_related()

            serializer = FilterMemberSerializer(query_set, many=True)

            paginated_data = paginate_data(request, serializer.data)

            return self.response_handler.handle(data=paginated_data)
        except Exception as exception:
            return self.exception_handler.handle(exception)

    @csrf_exempt
    @action(methods=['POST'], url_path='not_member_filter', detail=False)
    def not_member_filter(self, request):
        """Get a list of not-member

        Args:
            + role_name_list: String <role_name>,<role_name> ['MEMBER', 'SUPER_MANAGER', 'STAFF']
        """

        
        accept_fields = [
            'role_name_list',
        ]

        try:
            request_extractor = self.request_handler.handle(request)
            receive_fields = request_extractor.data
            accepted_fields = dict()

            for key in receive_fields.keys():
                if key in accept_fields:
                    accepted_fields[key] = receive_fields[key]

            validator = UserValidator(**accepted_fields)
            validator.is_missing_fields(['role_name_list',])

            validator.is_valid_fields([
                'role_name_list',
            ])

            dict_to_filter_user = validator.get_data(['role_name_list',])

            dict_to_filter_user.setdefault('order_by', '-created_at')

            query_set = CustomUser.objects.all()

            filter = UserFilter(dict_to_filter_user, queryset=query_set)

            query_set = filter.qs

            query_set = query_set.select_related()

            serializer = FilterNotMemberSerializer(query_set, many=True)

            return self.response_handler.handle(data=serializer.data)
        except Exception as exception:
            return self.exception_handler.handle(exception)

class HomeAPI(AbstractView):

    permission_classes = [permissions.IsAuthenticated]

    @csrf_exempt
    @action(methods=['POST'], url_path='manager', detail=False)
    def manager_home(self, request):
        """Get informations to display home screen for manager

        Args:
            None
        """

        try:

            users_query_set = CustomUser.objects.all()
            tests_query_set = Test.objects.all()

            # Calculate number of waiting users

            dict_to_filter_waiting_users = {
                'role_name': 'MEMBER',
                'status': CustomUserStatus.WAITING,
            }

            filter = UserFilter(dict_to_filter_waiting_users, queryset=users_query_set)

            number_of_waiting_users = filter.qs.count()

            # Calculate number of suspected users

            dict_to_filter_suspected_users = {
                'role_name': 'MEMBER',
                'health_status_list': f'{HealthStatus.UNWELL},{HealthStatus.SERIOUS}',
            }

            filter = UserFilter(dict_to_filter_suspected_users, queryset=users_query_set)

            number_of_suspected_users = filter.qs.count()

            # Calculate number of need test users

            test_day = int(os.environ.get('TEST_DAY_DEFAULT', 5))
            last_tested_max = str(datetime.datetime.now() - datetime.timedelta(days=test_day))

            dict_to_filter_need_test_users = {
                'role_name': 'MEMBER',
                'last_tested_max': last_tested_max,
            }

            filter = UserFilter(dict_to_filter_need_test_users, queryset=users_query_set)

            number_of_need_test_users = filter.qs.count()

            # Calculate number of can finish users

            positive_test = 'false'
            health_status_list = HealthStatus.NORMAL
            quarantine_day = int(os.environ.get('QUARANTINE_DAY_DEFAULT', 14))
            quarantined_at_max = datetime.datetime.now() - datetime.timedelta(days=quarantine_day)
            quarantined_at_max = timestamp_string_to_date_string(str(quarantined_at_max))

            dict_to_filter_can_finish_users = {
                'role_name': 'MEMBER',
                'positive_test': positive_test,
                'health_status_list': health_status_list,
                'quarantined_at_max': quarantined_at_max,
            }

            filter = UserFilter(dict_to_filter_can_finish_users, queryset=users_query_set)

            number_of_can_finish_users = filter.qs.count()

            # Calculate number of waiting tests

            dict_to_filter_waiting_tests = {
                'status': TestStatus.WAITING,
            }

            filter = TestFilter(dict_to_filter_waiting_tests, queryset=tests_query_set)

            number_of_waiting_tests = filter.qs.count()

            # Calculate number of member 'in' today

            dict_of_in_members = dict()

            for day_sub in range(3):
                day = datetime.datetime.now() - datetime.timedelta(days=day_sub)
                day = timestamp_string_to_date_string(str(day))

                dict_to_filter_in_members = {
                    'role_name': 'MEMBER',
                    'quarantined_at_max': day,
                    'quarantined_at_min': day,
                }

                filter = UserFilter(dict_to_filter_in_members, queryset=users_query_set)

                dict_of_in_members[f'{day}'] = filter.qs.count()

            # Calculate number of member 'out' today

            dict_of_out_members = dict()

            for day_sub in range(3):
                day = datetime.datetime.now() - datetime.timedelta(days=day_sub)
                day = timestamp_string_to_date_string(str(day))

                dict_to_filter_in_members = {
                    'role_name': 'MEMBER',
                    'quarantined_finished_at_max': day,
                    'quarantined_finished_at_min': day,
                }

                filter = UserFilter(dict_to_filter_in_members, queryset=users_query_set)

                dict_of_out_members[f'{day}'] = filter.qs.count()

            response_data = {
                'number_of_waiting_users': number_of_waiting_users,
                'number_of_suspected_users': number_of_suspected_users,
                'number_of_need_test_users': number_of_need_test_users,
                'number_of_can_finish_users': number_of_can_finish_users,
                'number_of_waiting_tests': number_of_waiting_tests,
                'in': dict_of_in_members,
                'out': dict_of_out_members,
            }

            return self.response_handler.handle(data=response_data)
        except Exception as exception:
            return self.exception_handler.handle(exception)
