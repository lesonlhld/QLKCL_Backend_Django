from rest_framework import serializers
from .models import CustomUser, Member
from address.serializers import (
    BaseCountrySerializer, BaseCitySerializer,
    BaseDistrictSerializer, BaseWardSerializer,
)
from quarantine_ward.serializers import (
    BaseQuarantineRoomSerializer, BaseQuarantineFloorSerializer,
    BaseQuarantineBuildingSerializer, BaseQuarantineWardSerializer,
)
from utils.tools import timestamp_string_to_date_string

class CustomUserSerializer(serializers.ModelSerializer):

    nationality = BaseCountrySerializer(many=False)
    country = BaseCountrySerializer(many=False)
    city = BaseCitySerializer(many=False)
    district = BaseDistrictSerializer(many=False)
    ward = BaseWardSerializer(many=False)

    class Meta:
        model = CustomUser
        exclude = ['password']

class BaseCustomUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = ['full_name', 'birthday']

class FilterMemberSerializer(serializers.ModelSerializer):

    quarantine_room = serializers.SerializerMethodField('get_quarantine_room')
    quarantine_floor = serializers.SerializerMethodField('get_quarantine_floor')
    quarantine_building = serializers.SerializerMethodField('get_quarantine_building')
    quarantine_ward = serializers.SerializerMethodField('get_quarantine_ward')

    health_status = serializers.SerializerMethodField('get_health_status')
    positive_test = serializers.SerializerMethodField('get_positive_test')
    last_tested = serializers.SerializerMethodField('get_last_tested')

    created_at = serializers.SerializerMethodField('get_created_at')

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

    def get_positive_test(self, custom_user):
        if hasattr(custom_user, 'member_x_custom_user'):
            return custom_user.member_x_custom_user.positive_test
        else:
            return None

    def get_last_tested(self, custom_user):
        if hasattr(custom_user, 'member_x_custom_user'):
            return custom_user.member_x_custom_user.last_tested
        else:
            return None

    def get_created_at(self, custom_user):
        created_at = str(custom_user.created_at)
        return timestamp_string_to_date_string(created_at)

    class Meta:
        model = CustomUser
        fields = [
            'full_name', 'gender', 'birthday', 'quarantine_room',
            'phone_number', 'created_at',
            'quarantine_floor', 'quarantine_building', 'quarantine_ward',
            'health_status', 'positive_test', 'last_tested',
        ]

class MemberSerializer(serializers.ModelSerializer):

    quarantine_room = BaseQuarantineRoomSerializer(many=False)
    quarantine_floor = BaseQuarantineFloorSerializer(many=False)
    quarantine_building = BaseQuarantineBuildingSerializer(many=False)
    quarantine_ward = BaseQuarantineWardSerializer(many=False)

    class Meta:
        model = Member
        fields = '__all__'