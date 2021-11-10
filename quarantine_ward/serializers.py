from rest_framework import serializers
from .models import (
    QuarantineWard, QuarantineBuilding,
    QuarantineFloor, QuarantineRoom,
)
from user_account.serializers import BaseCustomUserSerializer

class BaseQuarantineRoomSerializer(serializers.ModelSerializer):

    class Meta:
        model = QuarantineRoom
        fields = '__all__'

class BaseQuarantineFloorSerializer(serializers.ModelSerializer):

    class Meta:
        model = QuarantineFloor
        fields = '__all__'

class BaseQuarantineBuildingSerializer(serializers.ModelSerializer):

    class Meta:
        model = QuarantineBuilding
        fields = '__all__'

class BaseQuarantineWardSerializer(serializers.ModelSerializer):

    class Meta:
        model = QuarantineWard
        fields = '__all__'

class FilterQuarantineWardSerializer(serializers.ModelSerializer):

    main_manager = BaseCustomUserSerializer(many=False)

    class Meta:
        model = QuarantineWard
        fields = ['main_manager', 'full_name','created_at', 'updated_at']