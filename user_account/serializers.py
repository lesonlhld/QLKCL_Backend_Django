from rest_framework import serializers
from .models import CustomUser, Member, Manager, Staff
from address.serializers import (
    BaseCountrySerializer, BaseCitySerializer,
    BaseDistrictSerializer, BaseWardSerializer,
)
from quarantine_ward.serializers import (
    BaseQuarantineWardSerializer,
    BaseQuarantineRoomSerializer, BaseQuarantineFloorSerializer,
    BaseQuarantineBuildingSerializer, BaseQuarantineWardSerializer,
    QuarantineWardSerializer,
)

from role.serializers import RoleSerializer, BaseRoleSerializer

from utils.tools import timestamp_string_to_date_string

class CustomUserSerializer(serializers.ModelSerializer):

    nationality = BaseCountrySerializer(many=False)
    country = BaseCountrySerializer(many=False)
    city = BaseCitySerializer(many=False)
    district = BaseDistrictSerializer(many=False)
    ward = BaseWardSerializer(many=False)
    quarantine_ward = BaseQuarantineWardSerializer(many=False)
    role = BaseRoleSerializer(many=False)

    class Meta:
        model = CustomUser
        exclude = ['password']

class BaseBaseCustomUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = ['code', 'full_name',]

class BaseCustomUserSerializer(serializers.ModelSerializer):

    health_status = serializers.SerializerMethodField('get_health_status')

    def get_health_status(self, custom_user):
        if hasattr(custom_user, 'member_x_custom_user'):
            return custom_user.member_x_custom_user.health_status
        elif hasattr(custom_user, 'manager_x_custom_user'):
            return custom_user.manager_x_custom_user.health_status
        elif hasattr(custom_user, 'staff_x_custom_user'):
            return custom_user.staff_x_custom_user.health_status
        else:
            return None

    class Meta:
        model = CustomUser
        fields = ['code', 'full_name', 'birthday', 'gender', 'health_status',]

class FilterMemberSerializer(serializers.ModelSerializer):

    quarantine_room = serializers.SerializerMethodField('get_quarantine_room')
    quarantine_floor = serializers.SerializerMethodField('get_quarantine_floor')
    quarantine_building = serializers.SerializerMethodField('get_quarantine_building')
    quarantine_ward = serializers.SerializerMethodField('get_quarantine_ward')

    health_status = serializers.SerializerMethodField('get_health_status')
    positive_test_now = serializers.SerializerMethodField('get_positive_test_now')
    last_tested = serializers.SerializerMethodField('get_last_tested')
    last_tested_had_result = serializers.SerializerMethodField('get_last_tested_had_result')

    created_at = serializers.SerializerMethodField('get_created_at')
    quarantined_at = serializers.SerializerMethodField('get_quarantined_at')

    label = serializers.SerializerMethodField('get_label')

    number_of_vaccine_doses = serializers.SerializerMethodField('get_number_of_vaccine_doses')

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

    def get_quarantine_ward(self, custom_user):
        if hasattr(custom_user, 'member_x_custom_user') and custom_user.member_x_custom_user.quarantine_ward:
            return BaseQuarantineWardSerializer(custom_user.member_x_custom_user.quarantine_ward, many=False).data
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
            'code', 'status',
            'full_name', 'gender', 'birthday', 'quarantine_room',
            'phone_number', 'created_at', 'quarantined_at',
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

    quarantine_room = serializers.SerializerMethodField('get_quarantine_room')
    quarantine_floor = serializers.SerializerMethodField('get_quarantine_floor')
    quarantine_building = serializers.SerializerMethodField('get_quarantine_building')
    quarantine_ward = serializers.SerializerMethodField('get_quarantine_ward')
    custom_user = serializers.SerializerMethodField('get_custom_user')
    health_status = serializers.SerializerMethodField('get_health_status')
    positive_test_now = serializers.SerializerMethodField('get_positive_test_now')
    last_tested = serializers.SerializerMethodField('get_last_tested')
    last_tested_had_result = serializers.SerializerMethodField('get_last_tested_had_result')
    created_at = serializers.SerializerMethodField('get_created_at')
    quarantined_at = serializers.SerializerMethodField('get_quarantined_at')

    def get_custom_user(self, custom_user):
        if hasattr(custom_user, 'member_x_custom_user') and custom_user.member_x_custom_user:
            return BaseCustomUserSerializer(custom_user, many=False).data
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

    def get_quarantine_ward(self, custom_user):
        if hasattr(custom_user, 'member_x_custom_user') and custom_user.member_x_custom_user.quarantine_ward:
            return QuarantineWardSerializer(custom_user.member_x_custom_user.quarantine_ward, many=False).data
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

    class Meta:
        model = Member
        fields = '__all__'

class ManagerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Manager
        fields = '__all__'

class StaffSerializer(serializers.ModelSerializer):

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

    class Meta:
        model = CustomUser
        fields = [
            'code', 'status',
            'full_name', 'gender', 'birthday',
            'phone_number', 'created_at',
            'quarantine_ward', 'care_area',
        ]