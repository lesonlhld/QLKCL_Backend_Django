from rest_framework import serializers
from .models import (
    QuarantineWard, QuarantineBuilding,
    QuarantineFloor, QuarantineRoom,
)

class BaseQuarantineRoomSerializer(serializers.ModelSerializer):

    class Meta:
        model = QuarantineRoom
        fields = ['id', 'name']

class BaseQuarantineFloorSerializer(serializers.ModelSerializer):

    class Meta:
        model = QuarantineFloor
        fields = ['id', 'name']

class BaseQuarantineBuildingSerializer(serializers.ModelSerializer):

    class Meta:
        model = QuarantineBuilding
        fields = ['id', 'name']

class BaseQuarantineWardSerializer(serializers.ModelSerializer):

    class Meta:
        model = QuarantineWard
        fields = ['id', 'full_name']
