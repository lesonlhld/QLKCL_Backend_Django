import os
import datetime, pytz
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Count, Avg
from rest_framework import permissions
from rest_framework.decorators import action, permission_classes
from .validators.user import UserValidator
from .models import CustomUser, Member, Manager, Staff
from .serializers import (
    CustomUserSerializer, MemberSerializer,
    FilterMemberSerializer, FilterNotMemberSerializer,
    MemberHomeSerializer, ManagerSerializer,
    StaffSerializer, FilterStaffSerializer,
)
from .filters.member import MemberFilter
from .filters.user import UserFilter
from .filters.staff import StaffFilter
from form.models import Test
from form.filters.test import TestFilter
from role.models import Role
from quarantine_ward.models import QuarantineRoom
from quarantine_ward.serializers import (
    QuarantineRoomSerializer, QuarantineFloorSerializer,
    QuarantineBuildingSerializer, BaseQuarantineWardSerializer,
)
from utils import exceptions, messages
from utils.enums import CustomUserStatus, HealthStatus, TestStatus, MemberQuarantinedStatus
from utils.views import AbstractView, paginate_data
from utils.tools import custom_user_code_generator

# Create your views here.

class MemberAPI(AbstractView):

    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.action == 'register_member':
            self.permission_classes = [permissions.AllowAny]
        return super().get_permissions()

    def is_room_full(self, room):
        return room.member_x_quarantine_room.all().count() >= room.capacity

    def is_pass_max_day_quarantined(self, room, max_day_had_quarantined_in_room):
        # All members in this room must have quarantined at most 1 day ago.
        time_now = timezone.now()
        for member in list(room.member_x_quarantine_room.all()):
            if member.quarantined_at and member.quarantined_at < time_now - datetime.timedelta(days=max_day_had_quarantined_in_room):
                return False
        return True

    def count_members_same_label(self, room, label):
        if not label:
            return 0
        return room.member_x_quarantine_room.all().filter(label=label).count()

    def count_average_number_of_vaccine_doses(self, room):
        return_value = room.member_x_quarantine_room.all().aggregate(Avg('number_of_vaccine_doses'))['number_of_vaccine_doses__avg']
        if not return_value:
            # Nobody in room
            return_value = 1
        return return_value

    def count_members_same_gender(self, room, gender):
        if not gender:
            return 0
        return room.member_x_quarantine_room.all().filter(custom_user__gender=gender).count()

    def count_available_slot(self, room):
        return room.capacity - room.member_x_quarantine_room.all().count()

    def get_suitable_room_for_member(self, input_dict):
        """input_dict.keys() = [
            quarantine_ward
            gender
            label
            number_of_vaccine_doses
            old_quarantine_room (can None)
        ]
        default, all field is not None

        """

        return_dict = dict()
        return_dict['room'] = None
        return_dict['warning'] = None

        if input_dict['old_quarantine_room']:
            return_dict['room'] = input_dict['old_quarantine_room']
            return_dict['warning'] = 'This room is current room of this member'
            return return_dict

        rooms = list(QuarantineRoom.objects.filter(quarantine_floor__quarantine_building__quarantine_ward = input_dict['quarantine_ward']))

        remain_rooms = [room for room in rooms if not self.is_room_full(room)]
        if len(remain_rooms) > 0:
            rooms = remain_rooms
        else:
            return_dict['room'] = None
            return_dict['warning'] = 'All rooms in this quarantine ward are full'
            return return_dict

        tieu_chi = ['max_day_quarantined', 'label', 'vaccine', 'gender', 'less_slot']
        # max_day_quarantined: All members in this room must have quarantined at most 1 day ago.
        # label: This room must have at most number of members that is same label as this member.
        # vaccine: This room must have minimum average abs(this.number_of_vaccine_doses - another_member.number_of_vaccine_doses)
        # gender: This room must have at most number of members that is same gender as this member.
        # less_slot: This room must have at less number of available slot.

        # tieu_chi max_day_quarantined
        max_day_had_quarantined_in_room = int(os.environ.get('MAX_DAY_HAD_QUARANTINED_IN_ROOM', 1))
        remain_rooms = [room for room in rooms if self.is_pass_max_day_quarantined(room, max_day_had_quarantined_in_room)]
        if len(remain_rooms) > 0:
            rooms = remain_rooms
        else:
            return_dict['room'] = None
            return_dict['warning'] = 'Not have a room satisfy max_day_quarantined'
            return return_dict

        # tieu_chi label
        count_each_room = [self.count_members_same_label(room, input_dict['label']) for room in rooms]
        max_same_label_in_room = max(count_each_room)
        remain_rooms = [rooms[i] for i in range(len(rooms)) if count_each_room[i] == max_same_label_in_room]
        rooms = remain_rooms
        
        # tieu_chi vaccine
        difference_each_room = [abs(self.count_average_number_of_vaccine_doses(room) - input_dict['number_of_vaccine_doses']) for room in rooms]
        min_difference_each_room = min(difference_each_room)
        remain_rooms = [rooms[i] for i in range(len(rooms)) if difference_each_room[i] == min_difference_each_room]
        rooms = remain_rooms

        # tieu_chi gender
        count_each_room = [self.count_members_same_gender(room, input_dict['gender']) for room in rooms]
        max_same_gender_in_room = max(count_each_room)
        remain_rooms = [rooms[i] for i in range(len(rooms)) if count_each_room[i] == max_same_gender_in_room]
        rooms = remain_rooms

        # tieu_chi less_slot
        count_each_room = [self.count_available_slot(room) for room in rooms]
        min_available_slot = min(count_each_room)
        remain_rooms = [rooms[i] for i in range(len(rooms)) if count_each_room[i] == min_available_slot]
        rooms = remain_rooms

        return_dict['room'] = rooms[0]
        return_dict['warning'] = None
        return return_dict

    def check_room_for_member(self, user, room):
        # Check if this member can be set to this room
        if not hasattr(user, 'member_x_custom_user') or user.role.name != 'MEMBER':
            return messages.ISNOTMEMBER
        if user.member_x_custom_user.quarantine_room == room:
            return messages.SUCCESS
        if room.quarantine_floor.quarantine_building.quarantine_ward != user.quarantine_ward:
            return 'This room is not in the quarantine ward of this user'
        if self.is_room_full(room):
            return 'This room is full'
        max_day_had_quarantined_in_room = int(os.environ.get('MAX_DAY_HAD_QUARANTINED_IN_ROOM', 1))
        if not self.is_pass_max_day_quarantined(room, max_day_had_quarantined_in_room):
            return 'This room does not satisfy max_day_quarantined'
        return messages.SUCCESS

    def get_suitable_care_staff_for_member(self, input_dict):
        """input_dict.keys() = [
            quarantine_floor
        ]
        default, all field is not None
        """

        return_dict = dict()
        return_dict['care_staff'] = None
        return_dict['warning'] = None

        query_set = Staff.objects.filter(
            care_area__icontains=input_dict['quarantine_floor'].id,
            custom_user__status=CustomUserStatus.AVAILABLE,
            custom_user__quarantine_ward=input_dict['quarantine_floor'].quarantine_building.quarantine_ward,
        )
        try:
            return_dict['care_staff'] = query_set.annotate(num_care_member=Count('custom_user__member_x_care_staff')).order_by('num_care_member')[:1].get().custom_user
        except Exception as exception:
            return_dict['warning'] = 'Cannot set care_staff for this member'
        return return_dict

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
            custom_user.code = custom_user_code_generator(custom_user.quarantine_ward.id)
            while (validator.is_code_exist(custom_user.code)):
                custom_user.code = custom_user_code_generator(custom_user.quarantine_ward.id)
            
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
            + gender: String ['MALE', 'FEMALE']
            + nationality_code: String
            + country_code: String
            + city_id: int
            + district_id: int
            + ward_id: int
            + detail_address: String
            - health_insurance_number: String
            - identity_number: String
            - passport_number: String
            + quarantine_ward_id: int
            - quarantine_room_id: int
            - label: String ['F0', 'F1', 'F2', 'F3', 'FROM_EPIDEMIC_AREA', 'ABROAD']
            - quarantined_at: String vd:'2000-01-26T01:23:45.123456Z'
            - positive_tested_before: boolean
            - background_disease: String '<id>,<id>,<id>'
            - other_background_disease: String
            - care_staff_code: String
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
            'care_staff_code',
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
            'care_staff_code',
        ]

        try:
            if request.user.role.name not in ['ADMINISTRATOR', 'SUPER_MANAGER', 'MANAGER', 'STAFF']:
                raise exceptions.AuthenticationException({'main': messages.NO_PERMISSION})

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
            [
                'nationality', 'country', 'city', 'district', 'ward',
                'quarantine_ward',
            ]

            dict_to_create_custom_user = validator.get_data(list_to_create_custom_user)

            custom_user = CustomUser(**dict_to_create_custom_user)
            custom_user.set_password('123456')
            custom_user.code = custom_user_code_generator(custom_user.quarantine_ward.id)
            while (validator.is_code_exist(custom_user.code)):
                custom_user.code = custom_user_code_generator(custom_user.quarantine_ward.id)
            custom_user.created_by = request.user
            custom_user.updated_by = request.user
            custom_user.role = Role.objects.get(name='MEMBER')

            # create Member

            list_to_create_member = [key for key in accepted_fields.keys() if key in member_fields]
            list_to_create_member = set(list_to_create_member) - \
            {'quarantine_room_id', 'care_staff_code'}
            list_to_create_member = list(list_to_create_member) + \
            ['care_staff',]

            dict_to_create_member = validator.get_data(list_to_create_member)

            member = Member(**dict_to_create_member)
            member.custom_user = custom_user
            if 'quarantined_at' not in accepted_fields.keys():
                member.quarantined_at = timezone.now()

            # extra set room for this member
            if hasattr(validator, '_quarantine_room'):
                # this field is received and not None
                quarantine_room = validator.get_field('quarantine_room')
                check_room_result = self.check_room_for_member(custom_user, quarantine_room)
                if check_room_result != messages.SUCCESS:
                    raise exceptions.ValidationException({'quarantine_room_id': check_room_result})
            else:
                input_dict_for_get_suitable_room = dict()
                input_dict_for_get_suitable_room['quarantine_ward'] = custom_user.quarantine_ward
                input_dict_for_get_suitable_room['gender'] = custom_user.gender
                input_dict_for_get_suitable_room['label'] = member.label
                input_dict_for_get_suitable_room['old_quarantine_room'] = None

                suitable_room_dict = self.get_suitable_room_for_member(input_dict=input_dict_for_get_suitable_room)
                quarantine_room = suitable_room_dict['room']
                warning = suitable_room_dict['warning']
                if not quarantine_room:
                    raise exceptions.ValidationException({'main': warning})

            member.quarantine_room = quarantine_room

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

            if hasattr(custom_user, 'member_x_custom_user'):
                member = custom_user.member_x_custom_user
                member_serializer = MemberSerializer(member, many=False)

                response_data['member'] = member_serializer.data

            if hasattr(custom_user, 'manager_x_custom_user'):
                manager = custom_user.manager_x_custom_user
                manager_serializer = ManagerSerializer(manager, many=False)

                response_data['manager'] = manager_serializer.data

            if hasattr(custom_user, 'staff_x_custom_user'):
                staff = custom_user.staff_x_custom_user
                staff_serializer = StaffSerializer(staff, many=False)

                response_data['staff'] = staff_serializer.data
            
            return self.response_handler.handle(data=response_data)
        
        except Exception as exception:
            return self.exception_handler.handle(exception)

    @csrf_exempt
    @action(methods=['POST'], url_path='update', detail=False)
    def update_member(self, request):
        """Update a member, if dont get code, will update member sending request

        Args:
            - code: int
            - full_name: String
            - email: String
            - birthday: String 'dd/mm/yyyy'
            - gender: String ['MALE', 'FEMALE']
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
            - label: String ['F0', 'F1', 'F2', 'F3', 'FROM_EPIDEMIC_AREA', 'ABROAD']
            - quarantined_at: String vd:'2000-01-26T01:23:45.123456Z'
            - positive_tested_before: boolean
            - background_disease: String '<id>,<id>,<id>'
            - other_background_disease: String
            - care_staff_code: String
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
            'care_staff_code',
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
            'care_staff_code',
        ]

        try:
            request_extractor = self.request_handler.handle(request)
            receive_fields = request_extractor.data
            accepted_fields = dict()

            for key in receive_fields.keys():
                if key in accept_fields:
                    accepted_fields[key] = receive_fields[key]

            if 'code' not in accepted_fields.keys():
                accepted_fields['code'] = request.user.code

            validator = UserValidator(**accepted_fields)
            validator.is_valid_fields([
                'email', 'birthday', 'gender', 'passport_number',
                'health_insurance_number', 'identity_number',
                'label', 'quarantined_at', 'positive_tested_before',
                'background_disease',
            ])
            validator.extra_validate_to_update_member()

            # update CustomUser

            custom_user = validator.get_field('custom_user')

            if request.user.role.name == 'MEMBER' and request.user != custom_user:
                raise exceptions.AuthenticationException({'main': messages.NO_PERMISSION})

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
                {'quarantine_room_id', 'care_staff_code',}
                list_to_update_member = list(list_to_update_member) + \
                ['quarantine_room', 'care_staff',]

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
    @action(methods=['POST'], url_path='accept_one', detail=False)
    def accept_one_member(self, request):
        """Accept one member

        Args:
            + code: String
            - quarantine_room_id: int
            - quarantined_at: String vd:'2000-01-26T01:23:45.123456Z'
            - care_staff_code: String
        """

        accept_fields = [
            'code', 'quarantine_room_id',
            'quarantined_at', 'care_staff_code',
        ]

        require_fields = [
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
            validator.is_missing_fields(require_fields)
            validator.is_valid_fields(['quarantined_at'])

            validator.extra_validate_to_accept_one_member()

            # check member
            custom_user = validator.get_field('custom_user')
            quarantine_room = validator.get_field('quarantine_room')
            quarantined_at = validator.get_field('quarantined_at')
            care_staff = validator.get_field('care_staff')

            if custom_user.role.name != 'MEMBER' or not hasattr(custom_user, 'member_x_custom_user'):
                raise exceptions.ValidationException({'main': messages.ISNOTMEMBER})
            if custom_user.status != CustomUserStatus.WAITING:
                raise exceptions.ValidationException({'main': messages.ISNOTWAITING})

            must_not_empty_fields_of_custom_user = [
                'full_name', 'nationality', 'country', 'city', 'district',
                'ward', 'identity_number', 'quarantine_ward', 
            ]
            
            for field in must_not_empty_fields_of_custom_user:
                if not getattr(custom_user, field):
                    raise exceptions.ValidationException({field: messages.EMPTY})
            
            member = custom_user.member_x_custom_user

            # quarantined_at
            if quarantined_at:
                member.quarantined_at = quarantined_at
            else:
                member.quarantined_at = timezone.now()

            # room
            if not quarantine_room:
                # auto set room
                input_dict_for_get_suitable_room = dict()
                input_dict_for_get_suitable_room['quarantine_ward'] = custom_user.quarantine_ward
                input_dict_for_get_suitable_room['gender'] = custom_user.gender
                input_dict_for_get_suitable_room['label'] = member.label
                input_dict_for_get_suitable_room['old_quarantine_room'] = None

                suitable_room_dict = self.get_suitable_room_for_member(input_dict=input_dict_for_get_suitable_room)
                quarantine_room = suitable_room_dict['room']
                warning = suitable_room_dict['warning']
                if not quarantine_room:
                    raise exceptions.ValidationException({'main': warning})
                else:
                    member.quarantine_room = quarantine_room
            else:
                # check room received
                result = self.check_room_for_member(custom_user, quarantine_room)
                if result == messages.SUCCESS:
                    member.quarantine_room = quarantine_room
                else:
                    raise exceptions.ValidationException({'quarantine_room_id': result})

            # care_staff
            if not care_staff:
                if not member.care_staff:
                    # auto set care_staff
                    input_dict_for_get_care_staff = dict()
                    input_dict_for_get_care_staff['quarantine_floor'] = member.quarantine_room.quarantine_floor

                    suitable_care_staff_dict = self.get_suitable_care_staff_for_member(input_dict=input_dict_for_get_care_staff)
                    care_staff = suitable_care_staff_dict['care_staff']
                    warning = suitable_care_staff_dict['warning']
                    if care_staff:
                        member.care_staff = care_staff
            else:
                # check care_staff received
                if care_staff.quarantine_ward != custom_user.quarantine_ward:
                    raise exceptions.ValidationException({'care_staff_code': messages.NOT_IN_QUARANTINE_WARD_OF_MEMBER})
                member.care_staff = care_staff
            
            custom_user.status = CustomUserStatus.AVAILABLE
            custom_user.created_by = request.user
            custom_user.updated_by = request.user
            member.save()
            custom_user.save()

            return self.response_handler.handle(data=messages.SUCCESS)
        except Exception as exception:
            return self.exception_handler.handle(exception)
    @csrf_exempt
    @action(methods=['POST'], url_path='accept_many', detail=False)
    def accept_many_members(self, request):
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

            validator.extra_validate_to_accept_many_members()

            # accept members

            return_messages = dict()

            custom_users = validator.get_field('members')

            for custom_user in custom_users:
                if custom_user.role.name != 'MEMBER' or not hasattr(custom_user, 'member_x_custom_user'):
                    return_messages[custom_user.code] = messages.ISNOTMEMBER
                    continue

                if custom_user.status != CustomUserStatus.WAITING:
                    return_messages[custom_user.code] = messages.ISNOTWAITING
                    continue

                member = custom_user.member_x_custom_user

                must_not_empty_fields_of_custom_user = [
                    'full_name', 'nationality', 'country', 'city', 'district',
                    'ward', 'identity_number', 'quarantine_ward', 
                ]

                is_continue_another_custom_user = False
                for field in must_not_empty_fields_of_custom_user:
                    if not getattr(custom_user, field):
                        is_continue_another_custom_user = True
                        return_messages[custom_user.code] = f'{field}: {messages.EMPTY}'
                        break
                if is_continue_another_custom_user:
                    continue
                
                # set room
                if not member.quarantine_room:
                    input_dict_for_get_suitable_room = dict()
                    input_dict_for_get_suitable_room['quarantine_ward'] = custom_user.quarantine_ward
                    input_dict_for_get_suitable_room['gender'] = custom_user.gender
                    input_dict_for_get_suitable_room['label'] = member.label
                    input_dict_for_get_suitable_room['old_quarantine_room'] = None

                    suitable_room_dict = self.get_suitable_room_for_member(input_dict=input_dict_for_get_suitable_room)
                    quarantine_room = suitable_room_dict['room']
                    warning = suitable_room_dict['warning']
                    if not quarantine_room:
                        return_messages[custom_user.code] = warning
                        continue
                    else:
                        member.quarantine_room = quarantine_room

                # set care_staff
                if not member.care_staff:
                    input_dict_for_get_care_staff = dict()
                    input_dict_for_get_care_staff['quarantine_floor'] = member.quarantine_room.quarantine_floor

                    suitable_care_staff_dict = self.get_suitable_care_staff_for_member(input_dict=input_dict_for_get_care_staff)
                    care_staff = suitable_care_staff_dict['care_staff']
                    warning = suitable_care_staff_dict['warning']
                    if care_staff:
                        member.care_staff = care_staff

                custom_user.status = CustomUserStatus.AVAILABLE
                member.quarantined_at = timezone.now()
                custom_user.created_by = request.user
                custom_user.updated_by = request.user
                member.save()
                custom_user.save()
            
            return self.response_handler.handle(data=return_messages)
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
                if custom_user.role.name == 'MEMBER' and hasattr(custom_user, 'member_x_custom_user') and custom_user.status == CustomUserStatus.WAITING:
                    custom_user.status = CustomUserStatus.REFUSED
                    custom_user.updated_by = request.user
                    member = custom_user.member_x_custom_user
                    member.quarantine_room = None
                    custom_user.save()
                    member.save()

            return self.response_handler.handle(data=messages.SUCCESS)
        except Exception as exception:
            return self.exception_handler.handle(exception)

    @csrf_exempt
    @action(methods=['POST'], url_path='finish_quarantine', detail=False)
    def finish_quarantine_members(self, request):
        """Finish quarantine some members

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

            validator.extra_validate_to_finish_quarantine_member()

            # finish quarantine members

            custom_users = validator.get_field('members')

            for custom_user in custom_users:
                if hasattr(custom_user, 'member_x_custom_user'):
                    custom_user.updated_by = request.user
                    member = custom_user.member_x_custom_user
                    member.quarantined_status = MemberQuarantinedStatus.COMPLETED
                    member.quarantined_finished_at = timezone.now()
                    member.quarantine_room = None
                    custom_user.save()
                    member.save()
            
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
            - positive_test_now: boolean
            - is_last_tested: boolean - True để lọc những người cách ly đến hạn xét nghiệm, False hoặc không truyền đồng nghĩa không lọc
            - can_finish_quarantine: boolean - True để lọc những người cách ly có thể hoàn thành cách ly, False hoặc không truyền đồng nghĩa không lọc
            - created_at_max: String vd:'2000-01-26T01:23:45.123456Z'
            - created_at_min: String vd:'2000-01-26T01:23:45.123456Z'
            - quarantined_at_max: String vd:'2000-01-26T01:23:45.123456Z'
            - quarantined_at_min: String vd:'2000-01-26T01:23:45.123456Z'
            - quarantine_ward_id: String
            - quarantine_building_id: String
            - quarantine_floor_id: String
            - quarantine_room_id: String
            - label_list: String <label>,<label> ['F0', 'F1', 'F2', 'F3', 'FROM_EPIDEMIC_AREA', 'ABROAD']
            - page: int
            - page_size: int
            - search: String
        """

        accept_fields = [
            'status', 'health_status_list', 'positive_test_now',
            'is_last_tested', 'can_finish_quarantine',
            'created_at_max', 'created_at_min',
            'quarantined_at_max', 'quarantined_at_min',
            'quarantine_ward_id', 'quarantine_building_id',
            'quarantine_floor_id', 'quarantine_room_id',
            'label_list',
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
                'status', 'positive_test_now', 'health_status_list', 'is_last_tested',
                'can_finish_quarantine', 'created_at_max', 'created_at_min',
                'quarantined_at_max', 'quarantined_at_min', 'label_list',
            ])
            validator.extra_validate_to_filter_member()

            query_set = CustomUser.objects.all()

            list_to_filter_user = [key for key in accepted_fields.keys()]
            list_to_filter_user = set(list_to_filter_user) - \
            {'is_last_tested', 'page', 'page_size'}
            list_to_filter_user = list(list_to_filter_user) + \
            [
                'status', 'quarantined_status',
                'last_tested_max', 'role_name', 'quarantined_at_max',
                'positive_test_now', 'health_status_list',
            ]

            dict_to_filter_user = validator.get_data(list_to_filter_user)

            dict_to_filter_user.setdefault('order_by', '-created_at')

            filter = MemberFilter(dict_to_filter_user, queryset=query_set)

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
        """Get a list user of some role

        Args:
            + role_name_list: String <role_name>,<role_name> ['MEMBER', 'SUPER_MANAGER', 'MANAGER', 'ADMINISTRATOR', 'STAFF']
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

    @csrf_exempt
    @action(methods=['POST'], url_path='get_suitable_room', detail=False)
    def get_suitable_room(self, request):
        """Get a suitable room for a member

        Args:
            + quarantine_ward_id: int
            + gender: String ['MALE', 'FEMALE']
            + label: String ['F0', 'F1', 'F2', 'F3', 'FROM_EPIDEMIC_AREA', 'ABROAD']
            + number_of_vaccine_doses: int
            - old_quarantine_room_id: int
        """

        
        accept_fields = [
            'quarantine_ward_id', 'gender',
            'label', 'number_of_vaccine_doses',
            'old_quarantine_room_id',
        ]

        require_fields = [
            'quarantine_ward_id', 'gender',
            'label', 'number_of_vaccine_doses',
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
            validator.is_valid_fields(['gender', 'label', 'number_of_vaccine_doses'])

            validator.extra_validate_to_get_suitable_room()

            input_dict_for_get_suitable_room = validator.get_data([
                'quarantine_ward', 'gender',
                'label', 'number_of_vaccine_doses',
                'old_quarantine_room',
            ])

            return_value = self.get_suitable_room_for_member(input_dict=input_dict_for_get_suitable_room)
            room = return_value['room']
            warning = return_value['warning']

            return_dict = dict()
            return_dict['quarantine_room'] = None
            return_dict['warning'] = warning

            if room:
                serializer = QuarantineRoomSerializer(room, many=False)
                return_dict['quarantine_room'] = serializer.data
                floor = room.quarantine_floor
                serializer = QuarantineFloorSerializer(floor, many=False)
                return_dict['quarantine_floor'] = serializer.data
                building = floor.quarantine_building
                serializer = QuarantineBuildingSerializer(building, many=False)
                return_dict['quarantine_building'] = serializer.data
                ward = building.quarantine_ward
                serializer = BaseQuarantineWardSerializer(ward, many=False)
                return_dict['quarantine_ward'] = serializer.data

            return self.response_handler.handle(data=return_dict)
        except Exception as exception:
            return self.exception_handler.handle(exception)

class ManagerAPI(AbstractView):

    permission_classes = [permissions.IsAuthenticated]

    @csrf_exempt
    @action(methods=['POST'], url_path='create', detail=False)
    def create_manager(self, request):
        """Create a manager

        Args:
            + full_name: String
            + phone_number: String
            - email: String
            + birthday: String 'dd/mm/yyyy'
            + gender: String ['MALE', 'FEMALE']
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
        """

        accept_fields = [
            'full_name', 'phone_number', 'email',
            'birthday', 'gender', 'nationality_code',
            'country_code', 'city_id', 'district_id', 'ward_id',
            'detail_address', 'health_insurance_number',
            'identity_number', 'passport_number',
            'quarantine_ward_id',
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

        manager_fields = []

        try:
            if request.user.role.name not in ['ADMINISTRATOR', 'SUPER_MANAGER']:
                raise exceptions.AuthenticationException({'main': messages.NO_PERMISSION})
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
            ])
            validator.extra_validate_to_create_manager()

            # create CustomUser

            list_to_create_custom_user = [key for key in accepted_fields.keys() if key in custom_user_fields]
            list_to_create_custom_user = set(list_to_create_custom_user) - \
            {'nationality_code', 'country_code', 'city_id', 'district_id', 'ward_id', 'quarantine_ward_id'}
            list_to_create_custom_user = list(list_to_create_custom_user) + \
            ['nationality', 'country', 'city', 'district', 'ward', 'quarantine_ward']

            dict_to_create_custom_user = validator.get_data(list_to_create_custom_user)

            custom_user = CustomUser(**dict_to_create_custom_user)
            custom_user.set_password('123456')
            custom_user.code = custom_user_code_generator(custom_user.quarantine_ward.id)
            while (validator.is_code_exist(custom_user.code)):
                custom_user.code = custom_user_code_generator(custom_user.quarantine_ward.id)
            custom_user.created_by = request.user
            custom_user.updated_by = request.user
            custom_user.role = Role.objects.get(name='MANAGER')

            # create Manager

            manager = Manager()
            manager.custom_user = custom_user

            custom_user.save()
            manager.save()

            custom_user_serializer = CustomUserSerializer(custom_user, many=False)
            manager_serializer = ManagerSerializer(manager, many=False)
            
            response_data = dict()
            response_data['custom_user'] = custom_user_serializer.data
            response_data['manager'] = manager_serializer.data
            
            return self.response_handler.handle(data=response_data)
        except Exception as exception:
            return self.exception_handler.handle(exception)

    @csrf_exempt
    @action(methods=['POST'], url_path='update', detail=False)
    def update_manager(self, request):
        """Update a manager, if dont get code, will update manager sending request

        Args:
            - code: int
            - full_name: String
            - email: String
            - birthday: String 'dd/mm/yyyy'
            - gender: String ['MALE', 'FEMALE']
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
        """

        accept_fields = [
            'code', 'full_name', 'email',
            'birthday', 'gender', 'nationality_code',
            'country_code', 'city_id', 'district_id', 'ward_id',
            'detail_address', 'health_insurance_number',
            'identity_number', 'passport_number',
            'quarantine_ward_id',
        ]

        custom_user_fields = [
            'code', 'full_name', 'email',
            'birthday', 'gender', 'nationality_code',
            'country_code', 'city_id', 'district_id', 'ward_id',
            'detail_address', 'health_insurance_number',
            'identity_number', 'passport_number',
            'quarantine_ward_id',
        ]

        manager_fields = []

        try:
            request_extractor = self.request_handler.handle(request)
            receive_fields = request_extractor.data
            accepted_fields = dict()

            for key in receive_fields.keys():
                if key in accept_fields:
                    accepted_fields[key] = receive_fields[key]

            if 'code' not in accepted_fields.keys():
                accepted_fields['code'] = request.user.code

            validator = UserValidator(**accepted_fields)
            validator.is_valid_fields([
                'email', 'birthday', 'gender', 'passport_number',
                'health_insurance_number', 'identity_number',
            ])
            validator.extra_validate_to_update_manager()

            # update CustomUser

            custom_user = validator.get_field('custom_user')

            if request.user.role.name in ['STAFF', 'MEMBER']:
                raise exceptions.AuthenticationException({'main': messages.NO_PERMISSION})

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

            custom_user.save()

            if hasattr(custom_user, 'manager_x_custom_user') and custom_user.manager_x_custom_user:
                manager = custom_user.manager_x_custom_user
                manager_serializer = ManagerSerializer(manager, many=False)
                response_data['manager'] = manager_serializer.data

            return self.response_handler.handle(data=response_data)
        except Exception as exception:
            return self.exception_handler.handle(exception)

class StaffAPI(AbstractView):

    permission_classes = [permissions.IsAuthenticated]

    @csrf_exempt
    @action(methods=['POST'], url_path='create', detail=False)
    def create_staff(self, request):
        """Create a staff

        Args:
            + full_name: String
            + phone_number: String
            - email: String
            + birthday: String 'dd/mm/yyyy'
            + gender: String ['MALE', 'FEMALE']
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
            - care_area: String <id>,<id>,<id> trong đó <id> là id của tầng (QuarantineFloor)
        """

        accept_fields = [
            'full_name', 'phone_number', 'email',
            'birthday', 'gender', 'nationality_code',
            'country_code', 'city_id', 'district_id', 'ward_id',
            'detail_address', 'health_insurance_number',
            'identity_number', 'passport_number',
            'quarantine_ward_id', 'care_area',
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

        try:
            if request.user.role.name not in ['ADMINISTRATOR', 'SUPER_MANAGER', 'MANAGER']:
                raise exceptions.AuthenticationException({'main': messages.NO_PERMISSION})
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
                'care_area',
            ])
            validator.extra_validate_to_create_staff()

            # create CustomUser

            list_to_create_custom_user = [key for key in accepted_fields.keys() if key in custom_user_fields]
            list_to_create_custom_user = set(list_to_create_custom_user) - \
            {'nationality_code', 'country_code', 'city_id', 'district_id', 'ward_id', 'quarantine_ward_id'}
            list_to_create_custom_user = list(list_to_create_custom_user) + \
            ['nationality', 'country', 'city', 'district', 'ward', 'quarantine_ward']

            dict_to_create_custom_user = validator.get_data(list_to_create_custom_user)

            custom_user = CustomUser(**dict_to_create_custom_user)
            custom_user.set_password('123456')
            custom_user.code = custom_user_code_generator(custom_user.quarantine_ward.id)
            while (validator.is_code_exist(custom_user.code)):
                custom_user.code = custom_user_code_generator(custom_user.quarantine_ward.id)
            custom_user.created_by = request.user
            custom_user.updated_by = request.user
            custom_user.role = Role.objects.get(name='STAFF')

            # create Staff

            dict_to_create_staff = validator.get_data(['care_area'])
            staff = Staff(**dict_to_create_staff)
            staff.custom_user = custom_user

            custom_user.save()
            staff.save()

            custom_user_serializer = CustomUserSerializer(custom_user, many=False)
            staff_serializer = StaffSerializer(staff, many=False)
            
            response_data = dict()
            response_data['custom_user'] = custom_user_serializer.data
            response_data['staff'] = staff_serializer.data
            
            return self.response_handler.handle(data=response_data)
        except Exception as exception:
            return self.exception_handler.handle(exception)

    @csrf_exempt
    @action(methods=['POST'], url_path='update', detail=False)
    def update_staff(self, request):
        """Update a staff, if dont get code, will update staff sending request

        Args:
            - code: int
            - full_name: String
            - email: String
            - birthday: String 'dd/mm/yyyy'
            - gender: String ['MALE', 'FEMALE']
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
            - care_area: String <id>,<id>,<id> trong đó <id> là id của tầng (QuarantineFloor)
        """

        accept_fields = [
            'code', 'full_name', 'email',
            'birthday', 'gender', 'nationality_code',
            'country_code', 'city_id', 'district_id', 'ward_id',
            'detail_address', 'health_insurance_number',
            'identity_number', 'passport_number',
            'quarantine_ward_id', 'care_area',
        ]

        custom_user_fields = [
            'code', 'full_name', 'email',
            'birthday', 'gender', 'nationality_code',
            'country_code', 'city_id', 'district_id', 'ward_id',
            'detail_address', 'health_insurance_number',
            'identity_number', 'passport_number',
            'quarantine_ward_id',
        ]

        try:
            request_extractor = self.request_handler.handle(request)
            receive_fields = request_extractor.data
            accepted_fields = dict()

            for key in receive_fields.keys():
                if key in accept_fields:
                    accepted_fields[key] = receive_fields[key]

            if 'code' not in accepted_fields.keys():
                accepted_fields['code'] = request.user.code

            validator = UserValidator(**accepted_fields)
            validator.is_valid_fields([
                'email', 'birthday', 'gender', 'passport_number',
                'health_insurance_number', 'identity_number',
                'care_area',
            ])
            validator.extra_validate_to_update_staff()

            # update CustomUser

            custom_user = validator.get_field('custom_user')

            if request.user.role.name == 'MEMBER':
                raise exceptions.AuthenticationException({'main': messages.NO_PERMISSION})

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

            if hasattr(custom_user, 'staff_x_custom_user') and custom_user.staff_x_custom_user:
                staff = custom_user.staff_x_custom_user
                dict_to_update_staff = validator.get_data(['care_area'])

                for attr, value in dict_to_update_staff.items(): 
                    setattr(staff, attr, value)

                staff_serializer = StaffSerializer(staff, many=False)
                response_data['staff'] = staff_serializer.data

                staff.save()

            custom_user.save()  

            return self.response_handler.handle(data=response_data)
        except Exception as exception:
            return self.exception_handler.handle(exception)

    @csrf_exempt
    @action(methods=['POST'], url_path='filter', detail=False)
    def filter_staff(self, request):
        """Get a list of staffs

        Args:
            - status: String ['WAITING', 'REFUSED', 'LOCKED', 'AVAILABLE']
            - health_status_list: String <status>,<status> ['NORMAL', 'UNWELL', 'SERIOUS']
            - positive_test_now: boolean
            - is_last_tested: boolean - True để lọc những người cán bộ đến hạn xét nghiệm, False hoặc không truyền đồng nghĩa không lọc
            - created_at_max: String vd:'2000-01-26T01:23:45.123456Z'
            - created_at_min: String vd:'2000-01-26T01:23:45.123456Z'
            - quarantine_ward_id: int
            - care_area: String <id>,<id> (id của tầng)
            - page: int
            - page_size: int
            - search: String
            - order_by: String ['full_name', 'created_at'], mặc định sắp thứ tự theo số lượng người cách ly đang chăm sóc tăng dần
        """

        accept_fields = [
            'status', 'health_status_list', 'positive_test_now',
            'is_last_tested',
            'created_at_max', 'created_at_min',
            'quarantine_ward_id',
            'care_area',
            'page', 'page_size', 'search', 'order_by',
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
                'status', 'health_status_list', 'positive_test_now',
                'is_last_tested', 'care_area',
                'created_at_max', 'created_at_min',
            ])
            validator.extra_validate_to_filter_staff()

            query_set = CustomUser.objects.all()

            list_to_filter_staff = [key for key in accepted_fields.keys()]
            list_to_filter_staff = set(list_to_filter_staff) - \
            {'is_last_tested', 'page', 'page_size'}
            list_to_filter_staff = list(list_to_filter_staff) + \
            [
                'status',
                'last_tested_max', 'role_name',
            ]

            dict_to_filter_staff = validator.get_data(list_to_filter_staff)

            filter = StaffFilter(dict_to_filter_staff, queryset=query_set)

            query_set = filter.qs

            if 'order_by' not in dict_to_filter_staff.keys():
                query_set = query_set.annotate(num_care_member=Count('member_x_care_staff')).order_by('num_care_member')

            query_set = query_set.select_related()

            serializer = FilterStaffSerializer(query_set, many=True)

            paginated_data = paginate_data(request, serializer.data)

            return self.response_handler.handle(data=paginated_data)
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

            if request.user.role.name not in ['ADMINISTRATOR', 'SUPER_MANAGER', 'MANAGER', 'STAFF',]:
                raise exceptions.AuthenticationException()

            users_query_set = CustomUser.objects.all()
            tests_query_set = Test.objects.all()

            # Calculate number of waiting users

            dict_to_filter_waiting_users = {
                'role_name': 'MEMBER',
                'status': CustomUserStatus.WAITING,
                'quarantined_status': MemberQuarantinedStatus.QUARANTINING,
            }

            filter = MemberFilter(dict_to_filter_waiting_users, queryset=users_query_set)

            number_of_waiting_users = filter.qs.count()

            # Calculate number of suspected users

            dict_to_filter_suspected_users = {
                'role_name': 'MEMBER',
                'health_status_list': f'{HealthStatus.UNWELL},{HealthStatus.SERIOUS}',
                'status': CustomUserStatus.AVAILABLE,
                'quarantined_status': MemberQuarantinedStatus.QUARANTINING,
            }

            filter = MemberFilter(dict_to_filter_suspected_users, queryset=users_query_set)

            number_of_suspected_users = filter.qs.count()

            # Calculate number of need test users

            test_day = int(os.environ.get('TEST_DAY_DEFAULT', 5))
            last_tested_max = str(datetime.datetime.now() - datetime.timedelta(days=test_day))

            dict_to_filter_need_test_users = {
                'role_name': 'MEMBER',
                'last_tested_max': last_tested_max,
                'status': CustomUserStatus.AVAILABLE,
                'quarantined_status': MemberQuarantinedStatus.QUARANTINING,
            }

            filter = MemberFilter(dict_to_filter_need_test_users, queryset=users_query_set)

            number_of_need_test_users = filter.qs.count()

            # Calculate number of can finish users

            positive_test_now = 'false'
            health_status_list = HealthStatus.NORMAL
            quarantine_day = int(os.environ.get('QUARANTINE_DAY_DEFAULT', 14))
            quarantined_at_max = timezone.now() - datetime.timedelta(days=quarantine_day)

            dict_to_filter_can_finish_users = {
                'role_name': 'MEMBER',
                'positive_test_now': positive_test_now,
                'health_status_list': health_status_list,
                'quarantined_at_max': quarantined_at_max,
                'status': CustomUserStatus.AVAILABLE,
                'quarantined_status': MemberQuarantinedStatus.QUARANTINING,
            }

            filter = MemberFilter(dict_to_filter_can_finish_users, queryset=users_query_set)

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
                day = timezone.now() - datetime.timedelta(days=day_sub)
                day = day.astimezone(pytz.timezone('Asia/Saigon'))
                start_of_day = datetime.datetime(day.year, day.month, day.day)
                start_of_day = start_of_day.astimezone(pytz.timezone('Asia/Saigon'))
                end_of_day = datetime.datetime(day.year, day.month, day.day, 23, 59, 59, 999999)
                end_of_day = end_of_day.astimezone(pytz.timezone('Asia/Saigon'))

                dict_to_filter_in_members = {
                    'role_name': 'MEMBER',
                    'quarantined_at_max': end_of_day,
                    'quarantined_at_min': start_of_day,
                }

                filter = MemberFilter(dict_to_filter_in_members, queryset=users_query_set)

                dict_of_in_members[f'{day}'] = filter.qs.count()

            # Calculate number of member 'out' today

            dict_of_out_members = dict()

            for day_sub in range(3):
                day = timezone.now() - datetime.timedelta(days=day_sub)
                day = day.astimezone(pytz.timezone('Asia/Saigon'))
                start_of_day = datetime.datetime(day.year, day.month, day.day)
                start_of_day = start_of_day.astimezone(pytz.timezone('Asia/Saigon'))
                end_of_day = datetime.datetime(day.year, day.month, day.day, 23, 59, 59, 999999)
                end_of_day = end_of_day.astimezone(pytz.timezone('Asia/Saigon'))

                dict_to_filter_in_members = {
                    'role_name': 'MEMBER',
                    'quarantined_finished_at_max': end_of_day,
                    'quarantined_finished_at_min': start_of_day,
                }

                filter = MemberFilter(dict_to_filter_in_members, queryset=users_query_set)

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
    
    @csrf_exempt
    @action(methods=['POST'], url_path='member', detail=False)
    def member_home(self, request):
        """Get information to display home screen for member

        Args:
            None
        """

        try:
            if request.user.role.name not in ['MEMBER']:
                raise exceptions.AuthenticationException()

            member = request.user
            serializer = MemberHomeSerializer(member, many=False)

            return self.response_handler.handle(data=serializer.data)
        except Exception as exception:
            return self.exception_handler.handle(exception)
