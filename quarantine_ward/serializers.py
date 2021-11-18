from rest_framework import serializers
from django.db.models import Sum
from user_account.models import CustomUser, Member
from address.serializers import (
    BaseCountrySerializer, BaseCitySerializer,
    BaseDistrictSerializer, BaseWardSerializer,
)
from .models import (
    QuarantineWard, QuarantineBuilding,
    QuarantineFloor, QuarantineRoom,
)

class BaseCustomUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = ['code', 'full_name', 'birthday']

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

class QuarantineRoomSerializer(serializers.ModelSerializer):

    num_current_member = serializers.IntegerField(
        source='member_x_quarantine_room.count',
        read_only=True,
    )

    class Meta:
        model = QuarantineRoom
        fields = '__all__'

class QuarantineFloorSerializer(serializers.ModelSerializer):

    class Meta:
        model = QuarantineFloor
        fields = '__all__'

    def to_representation(self, instance):
        data =  super().to_representation(instance)

        data['num_current_member'] = Member.objects.filter(
            quarantine_room__quarantine_floor__id=data['id']
        ).count()

        total_capacity = QuarantineRoom.objects.filter(
            quarantine_floor__id=data['id']
        ).aggregate(Sum('capacity'))

        data['total_capacity'] = next(iter(total_capacity.values()))
        return data


class QuarantineBuildingSerializer(serializers.ModelSerializer):

    class Meta:
        model = QuarantineBuilding
        fields = '__all__'
    
    def to_representation(self, instance):
        data =  super().to_representation(instance)

        data['num_current_member'] = Member.objects.filter(
            quarantine_room__quarantine_floor__quarantine_building__id=data['id']
        ).count()

        total_capacity = QuarantineRoom.objects.filter(
            quarantine_floor__quarantine_building__id=data['id']
        ).aggregate(Sum('capacity'))

        data['total_capacity'] = next(iter(total_capacity.values()))
        return data

class QuarantineWardSerializer(serializers.ModelSerializer):

    main_manager = BaseCustomUserSerializer(many=False)
    country = BaseCountrySerializer(many=False)
    city = BaseCitySerializer(many=False)
    district = BaseDistrictSerializer(many=False)
    ward = BaseWardSerializer(many=False)

    class Meta:
        model = QuarantineWard
        fields = '__all__'
    
    def to_representation(self, instance):
        data =  super().to_representation(instance)

        data['num_current_member'] = Member.objects.filter(
            quarantine_room__quarantine_floor__quarantine_building__quarantine_ward__id=data['id']
        ).count()

        total_capacity = QuarantineRoom.objects.filter(
            quarantine_floor__quarantine_building__quarantine_ward__id=data['id']
        ).aggregate(Sum('capacity'))

        data['total_capacity'] = next(iter(total_capacity.values()))
        return data

class QuarantineWardWithBuildingSerializer(serializers.ModelSerializer):

    main_manager = BaseCustomUserSerializer(many=False) 

    class Meta:
        model = QuarantineWard
        fields = ['id', 'full_name', 'main_manager']

class QuarantineWardForRegisterSerializer(serializers.ModelSerializer):

    class Meta:
        model = QuarantineWard
        fields = ['id', 'full_name']

    def to_representation(self, instance):
        data =  super().to_representation(instance)

        num_current_member = Member.objects.filter(
            quarantine_room__quarantine_floor__quarantine_building__quarantine_ward__id=data['id']
        ).count()

        total_capacity = QuarantineRoom.objects.filter(
            quarantine_floor__quarantine_building__quarantine_ward__id=data['id']
        ).aggregate(Sum('capacity'))

        total_capacity = next(iter(total_capacity.values()))
        if total_capacity == None:
            total_capacity = 0

        if self.context == 'set_full':
            if num_current_member == total_capacity:
                return None

        return data

class FilterQuarantineWardSerializer(serializers.ModelSerializer):

    main_manager = BaseCustomUserSerializer(many=False)

    class Meta:
        model = QuarantineWard
        fields = ['id', 'main_manager', 'full_name','created_at', 'updated_at']
    
    def to_representation(self, instance):
        data =  super().to_representation(instance)

        data['num_current_member'] = Member.objects.filter(
            quarantine_room__quarantine_floor__quarantine_building__quarantine_ward__id=data['id']
        ).count()

        total_capacity = QuarantineRoom.objects.filter(
            quarantine_floor__quarantine_building__quarantine_ward__id=data['id']
        ).aggregate(Sum('capacity'))

        data['total_capacity'] = next(iter(total_capacity.values()))
        if data['total_capacity'] == None:
            data['total_capacity'] = 0

        if self.context == 'set_full':
            if data['num_current_member'] == data['total_capacity']:
                return None

        return data

class FilterQuarantineBuildingSerializer(serializers.ModelSerializer):

    quarantine_ward = QuarantineWardWithBuildingSerializer(many=False)

    class Meta:
        model = QuarantineBuilding
        fields = ['id', 'name', 'quarantine_ward']
    
    def to_representation(self, instance):
        data =  super().to_representation(instance)

        data['num_current_member'] = Member.objects.filter(
            quarantine_room__quarantine_floor__quarantine_building__id=data['id']
        ).count()

        total_capacity = QuarantineRoom.objects.filter(
            quarantine_floor__quarantine_building__id=data['id']
        ).aggregate(Sum('capacity'))

        data['total_capacity'] = next(iter(total_capacity.values()))
        if data['total_capacity'] == None:
            data['total_capacity'] = 0

        if self.context == 'set_full':
            if data['num_current_member'] == data['total_capacity']:
                return None
        return data

class FilterQuarantineFloorSerializer(serializers.ModelSerializer):

    quarantine_building = BaseQuarantineBuildingSerializer(many=False)

    class Meta:
        model = QuarantineFloor
        fields = ['id', 'name', 'quarantine_building']
    
    def to_representation(self, instance):
        data =  super().to_representation(instance)

        data['num_current_member'] = Member.objects.filter(
            quarantine_room__quarantine_floor__id=data['id']
        ).count()

        total_capacity = QuarantineRoom.objects.filter(
            quarantine_floor__id=data['id']
        ).aggregate(Sum('capacity'))

        data['total_capacity'] = next(iter(total_capacity.values()))
        if data['total_capacity'] == None:
            data['total_capacity'] = 0

        if self.context == 'set_full':
            if data['num_current_member'] == data['total_capacity']:
                return None

        return data

class FilterQuarantineRoomSerializer(serializers.ModelSerializer):

    quarantine_floor = BaseQuarantineFloorSerializer(many=False)
    num_current_member = serializers.IntegerField(
        source='member_x_quarantine_room.count',
        read_only=True,
    )

    class Meta:
        model = QuarantineRoom
        fields = ['id', 'name', 'capacity', 'quarantine_floor', 'num_current_member']
    
    def to_representation(self, instance):
        data =  super().to_representation(instance)

        if self.context == 'set_full':
            if data['num_current_member'] == data['capacity']:
                return None
                
        return data
