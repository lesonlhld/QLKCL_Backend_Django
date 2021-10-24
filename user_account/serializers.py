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

class CustomUserSerializer(serializers.ModelSerializer):

    nationality = BaseCountrySerializer(many=False)
    country = BaseCountrySerializer(many=False)
    city = BaseCitySerializer(many=False)
    district = BaseDistrictSerializer(many=False)
    ward = BaseWardSerializer(many=False)

    class Meta:
        model = CustomUser
        exclude = ['password']

class MemberSerializer(serializers.ModelSerializer):

    quarantine_room = BaseQuarantineRoomSerializer(many=False)
    quarantine_floor = BaseQuarantineFloorSerializer(many=False)
    quarantine_building = BaseQuarantineBuildingSerializer(many=False)
    quarantine_ward = BaseQuarantineWardSerializer(many=False)

    class Meta:
        model = Member
        fields = '__all__'