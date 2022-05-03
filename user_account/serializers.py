from rest_framework import serializers
from .models import CustomUser, Member, Manager, Staff, DestinationHistory, QuarantineHistory
from address.serializers import (
    BaseCountrySerializer, BaseCitySerializer,
    BaseDistrictSerializer, BaseWardSerializer,
)
from form.models import Pandemic
from quarantine_ward.models import QuarantineFloor
from quarantine_ward.serializers import (
    BaseQuarantineWardSerializer,
    BaseQuarantineRoomSerializer, BaseQuarantineFloorSerializer,
    BaseQuarantineBuildingSerializer, BaseQuarantineWardSerializer,
    QuarantineWardSerializer,
)

from role.serializers import RoleSerializer, BaseRoleSerializer

from utils import messages
from utils.enums import Professional
from utils.tools import timestamp_string_to_date_string, split_input_list

class CustomUserSerializer(serializers.ModelSerializer):

    nationality = BaseCountrySerializer(many=False)
    country = BaseCountrySerializer(many=False)
    city = BaseCitySerializer(many=False)
    district = BaseDistrictSerializer(many=False)
    ward = BaseWardSerializer(many=False)
    professional = serializers.SerializerMethodField('get_professional')

    def get_professional(self, custom_user):
        if custom_user.professional:
            reversed_professional_dict = {i.value: i.name for i in Professional}
            if custom_user.professional in reversed_professional_dict.keys():
                return {
                    'code': reversed_professional_dict[custom_user.professional],
                    'name': custom_user.professional,
                }
            else:
                return {
                    'code': messages.INVALID,
                    'name': custom_user.professional,
                }
        else:
            return None
    
    quarantine_ward = BaseQuarantineWardSerializer(many=False)
    role = BaseRoleSerializer(many=False)

    class Meta:
        model = CustomUser
        exclude = ['password']

class BaseBaseCustomUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = ['code', 'full_name', 'status']

class BaseCustomUserSerializer(serializers.ModelSerializer):

    health_status = serializers.SerializerMethodField('get_health_status')
    positive_test_now = serializers.SerializerMethodField('get_positive_test_now')

    def get_health_status(self, custom_user):
        if hasattr(custom_user, 'member_x_custom_user'):
            return custom_user.member_x_custom_user.health_status
        elif hasattr(custom_user, 'manager_x_custom_user'):
            return custom_user.manager_x_custom_user.health_status
        elif hasattr(custom_user, 'staff_x_custom_user'):
            return custom_user.staff_x_custom_user.health_status
        else:
            return None

    def get_positive_test_now(self, custom_user):
        if hasattr(custom_user, 'member_x_custom_user'):
            return custom_user.member_x_custom_user.positive_test_now
        elif hasattr(custom_user, 'manager_x_custom_user'):
            return custom_user.manager_x_custom_user.positive_test_now
        elif hasattr(custom_user, 'staff_x_custom_user'):
            return custom_user.staff_x_custom_user.positive_test_now
        else:
            return None

    class Meta:
        model = CustomUser
        fields = ['code', 'full_name', 'birthday', 'gender', 'status', 'health_status', 'positive_test_now']

class FilterMemberSerializer(serializers.ModelSerializer):

    quarantined_status = serializers.SerializerMethodField('get_quarantined_status')

    quarantine_room = serializers.SerializerMethodField('get_quarantine_room')
    quarantine_floor = serializers.SerializerMethodField('get_quarantine_floor')
    quarantine_building = serializers.SerializerMethodField('get_quarantine_building')
    quarantine_ward = BaseQuarantineWardSerializer(many=False)

    health_status = serializers.SerializerMethodField('get_health_status')
    positive_test_now = serializers.SerializerMethodField('get_positive_test_now')
    last_tested = serializers.SerializerMethodField('get_last_tested')
    last_tested_had_result = serializers.SerializerMethodField('get_last_tested_had_result')

    created_at = serializers.SerializerMethodField('get_created_at')
    quarantined_at = serializers.SerializerMethodField('get_quarantined_at')
    quarantined_finish_expected_at = serializers.SerializerMethodField('get_quarantined_finish_expected_at')
    quarantined_finished_at = serializers.SerializerMethodField('get_quarantined_finished_at')

    label = serializers.SerializerMethodField('get_label')

    number_of_vaccine_doses = serializers.SerializerMethodField('get_number_of_vaccine_doses')

    def get_quarantined_status(self, custom_user):
        if hasattr(custom_user, 'member_x_custom_user'):
            return custom_user.member_x_custom_user.quarantined_status
        else:
            return None

    def get_quarantine_room(self, custom_user):
        if hasattr(custom_user, 'member_x_custom_user') and custom_user.member_x_custom_user.quarantine_room:
            return BaseQuarantineRoomSerializer(custom_user.member_x_custom_user.quarantine_room, many=False).data
        else:
            return None
    
    def get_quarantine_floor(self, custom_user):
        if hasattr(custom_user, 'member_x_custom_user') and custom_user.member_x_custom_user.quarantine_floor:
            return BaseQuarantineFloorSerializer(custom_user.member_x_custom_user.quarantine_floor, many=False).data
        else:
            return None
    
    def get_quarantine_building(self, custom_user):
        if hasattr(custom_user, 'member_x_custom_user') and custom_user.member_x_custom_user.quarantine_building:
            return BaseQuarantineBuildingSerializer(custom_user.member_x_custom_user.quarantine_building, many=False).data
        else:
            return None

    def get_health_status(self, custom_user):
        if hasattr(custom_user, 'member_x_custom_user'):
            return custom_user.member_x_custom_user.health_status
        else:
            return None

    def get_positive_test_now(self, custom_user):
        if hasattr(custom_user, 'member_x_custom_user'):
            return custom_user.member_x_custom_user.positive_test_now
        else:
            return None

    def get_last_tested(self, custom_user):
        if hasattr(custom_user, 'member_x_custom_user'):
            return custom_user.member_x_custom_user.last_tested
        else:
            return None

    def get_last_tested_had_result(self, custom_user):
        if hasattr(custom_user, 'member_x_custom_user'):
            return custom_user.member_x_custom_user.last_tested_had_result
        else:
            return None

    def get_created_at(self, custom_user):
        created_at = str(custom_user.created_at)
        return timestamp_string_to_date_string(created_at)

    def get_quarantined_at(self, custom_user):
        if hasattr(custom_user, 'member_x_custom_user'):
            return custom_user.member_x_custom_user.quarantined_at
        else:
            return None

    def get_quarantined_finish_expected_at(self, custom_user):
        if hasattr(custom_user, 'member_x_custom_user'):
            return custom_user.member_x_custom_user.quarantined_finish_expected_at
        else:
            return None
    
    def get_quarantined_finished_at(self, custom_user):
        if hasattr(custom_user, 'member_x_custom_user'):
            return custom_user.member_x_custom_user.quarantined_finished_at
        else:
            return None

    def get_label(self, custom_user):
        if hasattr(custom_user, 'member_x_custom_user'):
            return custom_user.member_x_custom_user.label
        else:
            return None

    def get_number_of_vaccine_doses(self, custom_user):
        if hasattr(custom_user, 'member_x_custom_user'):
            return custom_user.member_x_custom_user.number_of_vaccine_doses
        else:
            return None

    class Meta:
        model = CustomUser
        fields = [
            'code', 'status', 'quarantined_status',
            'full_name', 'gender', 'birthday', 'quarantine_room',
            'phone_number', 'created_at', 'quarantined_at', 'quarantined_finish_expected_at',
            'quarantined_finished_at',
            'quarantine_floor', 'quarantine_building', 'quarantine_ward',
            'health_status', 'positive_test_now', 'last_tested',
            'last_tested_had_result', 'label', 'number_of_vaccine_doses',
        ]

class FilterNotMemberSerializer(serializers.ModelSerializer):

    role = RoleSerializer(many=False)

    class Meta:
        model = CustomUser
        fields = ['code', 'full_name', 'role', 'phone_number',]

class MemberSerializer(serializers.ModelSerializer):

    quarantine_room = BaseQuarantineRoomSerializer(many=False)
    quarantine_floor = BaseQuarantineFloorSerializer(many=False)
    quarantine_building = BaseQuarantineBuildingSerializer(many=False)
    quarantine_ward = BaseQuarantineWardSerializer(many=False)
    care_staff = BaseCustomUserSerializer(many=False)

    class Meta:
        model = Member
        fields = '__all__'

class MemberHomeSerializer(serializers.ModelSerializer):

    quarantine_room = BaseQuarantineRoomSerializer(many=False)
    quarantine_floor = BaseQuarantineFloorSerializer(many=False)
    quarantine_building = BaseQuarantineBuildingSerializer(many=False)
    quarantine_ward = serializers.SerializerMethodField('get_quarantine_ward')
    custom_user = BaseBaseCustomUserSerializer(many=False)
    care_staff = BaseCustomUserSerializer(many=False)

    def get_quarantine_ward(self, member):
        return QuarantineWardSerializer(member.custom_user.quarantine_ward, many=False).data

    class Meta:
        model = Member
        fields = '__all__'

class ManagerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Manager
        fields = '__all__'

class StaffSerializer(serializers.ModelSerializer):

    care_area = serializers.SerializerMethodField('get_care_area')

    def get_care_area(self, staff):
        list_of_floor_id = split_input_list(staff.care_area)
        return_list = []
        list_of_floor = list(QuarantineFloor.objects.filter(id__in=list_of_floor_id))
        for floor in list_of_floor:
            building = floor.quarantine_building
            ward = building.quarantine_ward
            return_list += [{
                'quarantine_floor': BaseQuarantineFloorSerializer(floor, many=False).data,
                'quarantine_building': BaseQuarantineBuildingSerializer(building, many=False).data,
                'quarantine_ward': BaseQuarantineWardSerializer(ward, many=False).data,
            }]
        return return_list

    class Meta:
        model = Staff
        fields = '__all__'

class FilterStaffSerializer(serializers.ModelSerializer):

    quarantine_ward = BaseQuarantineWardSerializer(many=False)

    care_area = serializers.SerializerMethodField('get_care_area')

    def get_care_area(self, custom_user):
        if hasattr(custom_user, 'staff_x_custom_user'):
            return custom_user.staff_x_custom_user.care_area
        else:
            return None

    num_care_member = serializers.SerializerMethodField('get_num_care_member')

    def get_num_care_member(self, custom_user):
        if hasattr(custom_user, 'num_care_member'):
            return custom_user.num_care_member
        else:
            return None

    class Meta:
        model = CustomUser
        fields = [
            'code', 'status',
            'full_name', 'gender', 'birthday',
            'phone_number', 'created_at',
            'quarantine_ward', 'care_area',
            'num_care_member',
        ]

class FilterManagerSerializer(serializers.ModelSerializer):

    quarantine_ward = BaseQuarantineWardSerializer(many=False)
    role = BaseRoleSerializer(many=False)

    class Meta:
        model = CustomUser
        fields = [
            'code', 'status',
            'full_name', 'gender', 'birthday',
            'phone_number', 'created_at',
            'quarantine_ward', 'role',
        ]

class DestinationHistorySerializer(serializers.ModelSerializer):

    user = BaseBaseCustomUserSerializer(many=False)
    country = BaseCountrySerializer(many=False)
    city = BaseCitySerializer(many=False)
    district = BaseDistrictSerializer(many=False)
    ward = BaseWardSerializer(many=False)

    class Meta:
        model = DestinationHistory
        fields = '__all__'

class BasePandemicSerializer(serializers.ModelSerializer):

    class Meta:
        model = Pandemic
        fields = ['id', 'name']

class BaseQuarantineHistorySerializer(serializers.ModelSerializer):

    user = BaseBaseCustomUserSerializer(many=False)
    quarantine_ward = BaseQuarantineWardSerializer(many=False)
    quarantine_building = serializers.SerializerMethodField('get_quarantine_building')
    quarantine_floor = serializers.SerializerMethodField('get_quarantine_floor')
    quarantine_room = BaseQuarantineRoomSerializer(many=False)

    def get_quarantine_floor(self, quarantine_history):
        if quarantine_history.quarantine_room:
            return BaseQuarantineFloorSerializer(quarantine_history.quarantine_room.quarantine_floor, many=False).data
        else:
            return None
    
    def get_quarantine_building(self, quarantine_history):
        if quarantine_history.quarantine_room:
            return BaseQuarantineBuildingSerializer(quarantine_history.quarantine_room.quarantine_floor.quarantine_building, many=False).data
        else:
            return None

    class Meta:
        model = QuarantineHistory
        fields = '__all__'

class QuarantineHistorySerializer(serializers.ModelSerializer):

    user = BaseBaseCustomUserSerializer(many=False)
    pandemic = BasePandemicSerializer(many=False)
    quarantine_ward = BaseQuarantineWardSerializer(many=False)
    quarantine_floor = serializers.SerializerMethodField('get_quarantine_floor')
    quarantine_building = serializers.SerializerMethodField('get_quarantine_building')
    quarantine_room = BaseQuarantineRoomSerializer(many=False)
    created_by = BaseBaseCustomUserSerializer(many=False)
    updated_by = BaseBaseCustomUserSerializer(many=False)

    def get_quarantine_floor(self, quarantine_history):
        if quarantine_history.quarantine_room:
            return BaseQuarantineFloorSerializer(quarantine_history.quarantine_room.quarantine_floor, many=False).data
        else:
            return None
    
    def get_quarantine_building(self, quarantine_history):
        if quarantine_history.quarantine_room:
            return BaseQuarantineBuildingSerializer(quarantine_history.quarantine_room.quarantine_floor.quarantine_building, many=False).data
        else:
            return None

    class Meta:
        model = QuarantineHistory
        fields = '__all__'
