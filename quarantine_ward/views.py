from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import action
from utils.views import AbstractView
from .models import (
    QuarantineWard,
    QuarantineBuilding,
    QuarantineFloor,
    QuarantineRoom,
)
from .serializers import (
    BaseQuarantineWardSerializer,
    BaseQuarantineBuildingSerializer,
    BaseQuarantineFloorSerializer,
    BaseQuarantineRoomSerializer,
)
from .validators.quarantine_ward import QuarantineWardValidator
from .validators.quarantine_building import QuarantineBuildingValidator
from .validators.quarantine_floor import QuarantineFloorValidator
from .validators.quarantine_room import QuarantineRoomValidator

class QuarantineWardAPI (AbstractView):
    
    @csrf_exempt
    @action(methods=['GET'], url_path='get', detail=False)
    def get_quarantineward(self, request):
        """Get a Quarantine Ward

        Args:
            + id (str)
        """

        accept_fields = [
            'id',
        ]

        require_fields = [
            'id',
        ]

        try:
            request_extractor = self.request_handler.handle(request)
            receive_fields = request_extractor.data
            accepted_fields = dict()

            for key in receive_fields:
                if key in accept_fields:
                    accepted_fields[key] = receive_fields[key]

            validator = QuarantineWardValidator(**accepted_fields)
            validator.is_missing_fields(require_fields)
            validator.is_valid_fields(accepted_fields)

            quarantine_ward = validator.get_field('id')

            serializer = BaseQuarantineWardSerializer(quarantine_ward, many=False)
            return self.response_handler.handle(data=serializer.data)
        except Exception as exception:
            return self.exception_handler.handle(exception)

    @csrf_exempt
    @action(methods=['POST'], url_path='create', detail=False)
    def create_quarantineward(self, request):
        """Create a Quarantine Ward

        Args:
            + email (str)
            + full_name (str)
            + country (str): country_id
            + city (str): city_id
            + district (str): district_id
            + ward (str): ward_id
            - address (str)
            - latitude (str)
            - longitude (str)
            - status (str)
            - type (str)
            - quarantine_time (int)
            + main_manager (str): id
        """

        accept_fields = [
            'email', 'full_name', 'country', 'city',
            'district', 'ward', 'address', 'latitude',
            'longitude', 'status', 'type', 'quarantine_time',
            'main_manager',
        ]

        require_fields = [
            'email', 'full_name', 'country', 'city',
            'district', 'ward','main_manager',
        ]

        try:
            request_extractor = self.request_handler.handle(request)
            receive_fields = request_extractor.data
            accepted_fields = dict()

            for key in receive_fields:
                if key in accept_fields:
                    accepted_fields[key] = receive_fields[key]

            validator = QuarantineWardValidator(**accepted_fields)
            
            validator.is_missing_fields(require_fields)
            validator.is_valid_fields(accepted_fields)
            list_to_create = accepted_fields.keys()
            dict_to_create = validator.get_data(list_to_create)
            quarantine_ward = QuarantineWard(**dict_to_create)
            quarantine_ward.save()

            serializer = BaseQuarantineWardSerializer(quarantine_ward, many=False)
            return self.response_handler.handle(data=serializer.data)
        except Exception as exception:
            return self.exception_handler.handle(exception)
    
    @csrf_exempt
    @action(methods=['POST'], url_path='update', detail=False)
    def update_quarantineward(self, request):
        """Update a Quarantine Ward

        Args:
            + id (str)
            - email (str)
            - full_name (str)
            - country (str): country_id
            - city (str): city_id
            - district (str): district_id
            - ward (str): ward_id
            - address (str)
            - latitude (str)
            - longitude (str)
            - status (str)
            - type (str)
            - quarantine_time (int)
            - main_manager (str): id
        """

        accept_fields = [
            'id', 'email', 'full_name', 'country', 'city',
            'district', 'ward', 'address', 'latitude',
            'longitude', 'status', 'type', 'quarantine_time',
            'main_manager',
        ]

        require_fields = [
            'id',
        ]

        try:
            request_extractor = self.request_handler.handle(request)
            receive_fields = request_extractor.data
            accepted_fields = dict()

            for key in receive_fields:
                if key in accept_fields:
                    accepted_fields[key] = receive_fields[key]
            validator = QuarantineWardValidator(**accepted_fields)
            validator.is_missing_fields(require_fields)
            validator.is_valid_fields(accepted_fields)
            quarantine_ward = validator.get_field('id')
            list_to_update = accepted_fields.keys() - {'id'}
            dict_to_update = validator.get_data(list_to_update)
            quarantine_ward.__dict__.update(**dict_to_update)
            quarantine_ward.save()
            serializer = BaseQuarantineWardSerializer(quarantine_ward, many=False)
            return self.response_handler.handle(data=serializer.data)
        except Exception as exception:
            return self.exception_handler.handle(exception)

    @csrf_exempt
    @action(methods=['POST'], url_path='delete', detail=False)
    def delete_quarantineward(self, request):
        """Delete a Quarantine Ward

        Args:
            + id (str)
        """

        accept_fields = [
            'id',
        ]

        require_fields = [
            'id',
        ]

        try:
            request_extractor = self.request_handler.handle(request)
            receive_fields = request_extractor.data
            accepted_fields = dict()

            for key in receive_fields:
                if key in accept_fields:
                    accepted_fields[key] = receive_fields[key]

            validator = QuarantineWardValidator(**accepted_fields)
            validator.is_missing_fields(require_fields)
            validator.is_valid_fields(accepted_fields)

            quarantine_ward = validator.get_field('id')
            quarantine_ward.delete()

            serializer = BaseQuarantineWardSerializer(quarantine_ward, many=False)
            return self.response_handler.handle(data=serializer.data)
        except Exception as exception:
            return self.exception_handler.handle(exception)
    
class QuarantineBuildingAPI (AbstractView):
    
    @csrf_exempt
    @action(methods=['GET'], url_path='get', detail=False)
    def get_quarantinebuilding(self, request):
        """Get a Quarantine Building

        Args:
            + id (str)
        """

        accept_fields = [
            'id',
        ]

        require_fields = [
            'id',
        ]

        try:
            request_extractor = self.request_handler.handle(request)
            receive_fields = request_extractor.data
            accepted_fields = dict()

            for key in receive_fields:
                if key in accept_fields:
                    accepted_fields[key] = receive_fields[key]

            validator = QuarantineBuildingValidator(**accepted_fields)
            validator.is_missing_fields(require_fields)
            validator.is_valid_fields(accepted_fields)

            quarantine_building = validator.get_field('id')

            serializer = BaseQuarantineBuildingSerializer(quarantine_building, many=False)
            return self.response_handler.handle(data=serializer.data)
        except Exception as exception:
            return self.exception_handler.handle(exception)

    @csrf_exempt
    @action(methods=['POST'], url_path='create', detail=False)
    def create_quarantinebuilding(self, request):
        """Create a Quarantine Building

        Args:
            + name (str)
            + quarantine_ward (str): id
        """

        accept_fields = [
            'name', 'quarantine_ward',
        ]

        require_fields = [
            'name', 'quarantine_ward',
        ]

        try:
            request_extractor = self.request_handler.handle(request)
            receive_fields = request_extractor.data
            accepted_fields = dict()

            for key in receive_fields:
                if key in accept_fields:
                    accepted_fields[key] = receive_fields[key]

            validator = QuarantineBuildingValidator(**accepted_fields)
            
            validator.is_missing_fields(require_fields)
            validator.is_valid_fields(accepted_fields)
            list_to_create = accepted_fields.keys()
            dict_to_create = validator.get_data(list_to_create)
            quarantine_building = QuarantineBuilding(**dict_to_create)
            quarantine_building.save()

            serializer = BaseQuarantineBuildingSerializer(quarantine_building, many=False)
            return self.response_handler.handle(data=serializer.data)
        except Exception as exception:
            return self.exception_handler.handle(exception)
    
    @csrf_exempt
    @action(methods=['POST'], url_path='update', detail=False)
    def update_quarantinebuilding(self, request):
        """Update a Quarantine Building

        Args:
            + id (str)
            - name (str)
            - quarantine_ward (str): id
        """

        accept_fields = [
            'id', 'name', 'quarantine_ward',
        ]

        require_fields = [
            'id',
        ]

        try:
            request_extractor = self.request_handler.handle(request)
            receive_fields = request_extractor.data
            accepted_fields = dict()

            for key in receive_fields:
                if key in accept_fields:
                    accepted_fields[key] = receive_fields[key]

            validator = QuarantineBuildingValidator(**accepted_fields)
            validator.is_missing_fields(require_fields)
            validator.is_valid_fields(accepted_fields)
            quarantine_building = validator.get_field('id')
            list_to_update = accepted_fields.keys() - {'id'}
            dict_to_update = validator.get_data(list_to_update)
            quarantine_building.__dict__.update(**dict_to_update)
            quarantine_building.save()

            serializer = BaseQuarantineBuildingSerializer(quarantine_building, many=False)
            return self.response_handler.handle(data=serializer.data)
        except Exception as exception:
            return self.exception_handler.handle(exception)

    @csrf_exempt
    @action(methods=['POST'], url_path='delete', detail=False)
    def delete_quarantinebuilding(self, request):
        """Delete a Quarantine Building

        Args:
            + id (str)
        """

        accept_fields = [
            'id',
        ]

        require_fields = [
            'id',
        ]

        try:
            request_extractor = self.request_handler.handle(request)
            receive_fields = request_extractor.data
            accepted_fields = dict()

            for key in receive_fields:
                if key in accept_fields:
                    accepted_fields[key] = receive_fields[key]

            validator = QuarantineBuildingValidator(**accepted_fields)
            validator.is_missing_fields(require_fields)
            validator.is_valid_fields(accepted_fields)

            quarantine_building = validator.get_field('id')
            quarantine_building.delete()

            serializer = BaseQuarantineBuildingSerializer(quarantine_building, many=False)
            return self.response_handler.handle(data=serializer.data)
        except Exception as exception:
            return self.exception_handler.handle(exception)

class QuarantineFloorAPI (AbstractView):
    
    @csrf_exempt
    @action(methods=['GET'], url_path='get', detail=False)
    def get_quarantinefloor(self, request):
        """Get a Quarantine Floor

        Args:
            + id (str)
        """

        accept_fields = [
            'id',
        ]

        require_fields = [
            'id',
        ]

        try:
            request_extractor = self.request_handler.handle(request)
            receive_fields = request_extractor.data
            accepted_fields = dict()

            for key in receive_fields:
                if key in accept_fields:
                    accepted_fields[key] = receive_fields[key]

            validator = QuarantineFloorValidator(**accepted_fields)
            validator.is_missing_fields(require_fields)
            validator.is_valid_fields(accepted_fields)

            quarantine_floor = validator.get_field('id')

            serializer = BaseQuarantineFloorSerializer(quarantine_floor, many=False)
            return self.response_handler.handle(data=serializer.data)
        except Exception as exception:
            return self.exception_handler.handle(exception)

    @csrf_exempt
    @action(methods=['POST'], url_path='create', detail=False)
    def create_quarantinefloor(self, request):
        """Create a Quarantine Floor

        Args:
            + name (str)
            + quarantine_building (str): id
        """

        accept_fields = [
            'name', 'quarantine_building',
        ]

        require_fields = [
            'name', 'quarantine_building',
        ]

        try:
            request_extractor = self.request_handler.handle(request)
            receive_fields = request_extractor.data
            accepted_fields = dict()

            for key in receive_fields:
                if key in accept_fields:
                    accepted_fields[key] = receive_fields[key]

            validator = QuarantineFloorValidator(**accepted_fields)
            
            validator.is_missing_fields(require_fields)
            validator.is_valid_fields(accepted_fields)
            list_to_create = accepted_fields.keys()
            dict_to_create = validator.get_data(list_to_create)
            quarantine_floor = QuarantineFloor(**dict_to_create)
            quarantine_floor.save()

            serializer = BaseQuarantineFloorSerializer(quarantine_floor, many=False)
            return self.response_handler.handle(data=serializer.data)
        except Exception as exception:
            return self.exception_handler.handle(exception)
    
    @csrf_exempt
    @action(methods=['POST'], url_path='update', detail=False)
    def update_quarantinefloor(self, request):
        """Update a Quarantine Floor

        Args:
            + id (str)
            - name (str)
            - quarantine_building (str): id
        """

        accept_fields = [
            'id', 'name', 'quarantine_building',
        ]

        require_fields = [
            'id',
        ]

        try:
            request_extractor = self.request_handler.handle(request)
            receive_fields = request_extractor.data
            accepted_fields = dict()

            for key in receive_fields:
                if key in accept_fields:
                    accepted_fields[key] = receive_fields[key]

            validator = QuarantineFloorValidator(**accepted_fields)
            validator.is_missing_fields(require_fields)
            validator.is_valid_fields(accepted_fields)
            quarantine_floor = validator.get_field('id')
            list_to_update = accepted_fields.keys() -{'id'}
            dict_to_update = validator.get_data(list_to_update)
            quarantine_floor.__dict__.update(**dict_to_update)
            quarantine_floor.save()

            serializer = BaseQuarantineFloorSerializer(quarantine_floor, many=False)
            return self.response_handler.handle(data=serializer.data)
        except Exception as exception:
            return self.exception_handler.handle(exception)

    @csrf_exempt
    @action(methods=['POST'], url_path='delete', detail=False)
    def delete_quarantinefloor(self, request):
        """Delete a Quarantine Floor

        Args:
            + id (str)
        """

        accept_fields = [
            'id',
        ]

        require_fields = [
            'id',
        ]

        try:
            request_extractor = self.request_handler.handle(request)
            receive_fields = request_extractor.data
            accepted_fields = dict()

            for key in receive_fields:
                if key in accept_fields:
                    accepted_fields[key] = receive_fields[key]

            validator = QuarantineFloorValidator(**accepted_fields)
            validator.is_missing_fields(require_fields)
            validator.is_valid_fields(accepted_fields)

            quarantine_floor = validator.get_field('id')
            quarantine_floor.delete()

            serializer = BaseQuarantineFloorSerializer(quarantine_floor, many=False)
            return self.response_handler.handle(data=serializer.data)
        except Exception as exception:
            return self.exception_handler.handle(exception)

class QuarantineRoomAPI(AbstractView):
    
    @csrf_exempt
    @action(methods=['GET'], url_path='get', detail=False)
    def get_quarantineroom(self, request):
        """Get a Quarantine Room

        Args:
            + id (str)
        """

        accept_fields = [
            'id',
        ]

        require_fields = [
            'id',
        ]

        try:
            request_extractor = self.request_handler.handle(request)
            receive_fields = request_extractor.data
            accepted_fields = dict()

            for key in receive_fields:
                if key in accept_fields:
                    accepted_fields[key] = receive_fields[key]

            validator = QuarantineRoomValidator(**accepted_fields)
            validator.is_missing_fields(require_fields)
            validator.is_valid_fields(accepted_fields)

            quarantine_room = validator.get_field('id')

            serializer = BaseQuarantineRoomSerializer(quarantine_room, many=False)
            return self.response_handler.handle(data=serializer.data)
        except Exception as exception:
            return self.exception_handler.handle(exception)

    @csrf_exempt
    @action(methods=['POST'], url_path='create', detail=False)
    def create_quarantineroom(self, request):
        """Create a Quarantine Room

        Args:
            + name (str)
            + capacity (int)
            + quarantine_floor (str): id
        """

        accept_fields = [
            'name', 'capacity', 'quarantine_floor',
        ]

        require_fields = [
            'name', 'quarantine_floor',
        ]

        try:
            request_extractor = self.request_handler.handle(request)
            receive_fields = request_extractor.data
            accepted_fields = dict()

            for key in receive_fields:
                if key in accept_fields:
                    accepted_fields[key] = receive_fields[key]

            validator = QuarantineRoomValidator(**accepted_fields)
            
            validator.is_missing_fields(require_fields)
            validator.is_valid_fields(accepted_fields)
            list_to_create = accepted_fields.keys()
            dict_to_create = validator.get_data(list_to_create)
            quarantine_room = QuarantineRoom(**dict_to_create)
            quarantine_room.save()

            serializer = BaseQuarantineRoomSerializer(quarantine_room, many=False)
            return self.response_handler.handle(data=serializer.data)
        except Exception as exception:
            return self.exception_handler.handle(exception)
    
    @csrf_exempt
    @action(methods=['POST'], url_path='update', detail=False)
    def update_quarantineroom(self, request):
        """Update a Quarantine Room

        Args:
            + id (str)
            - name (str)
            - capacity (int)
            - quarantine_floor (str): id
        """

        accept_fields = [
            'id', 'name', 'capacity', 'quarantine_floor',
        ]

        require_fields = [
            'id',
        ]

        try:
            request_extractor = self.request_handler.handle(request)
            receive_fields = request_extractor.data
            accepted_fields = dict()

            for key in receive_fields:
                if key in accept_fields:
                    accepted_fields[key] = receive_fields[key]

            validator = QuarantineRoomValidator(**accepted_fields)
            validator.is_missing_fields(require_fields)
            validator.is_valid_fields(accepted_fields)
            quarantine_room = validator.get_field('id')
            list_to_update = accepted_fields.keys() - {'id'}
            dict_to_update = validator.get_data(list_to_update)
            quarantine_room.__dict__.update(**dict_to_update)
            quarantine_room.save()

            serializer = BaseQuarantineRoomSerializer(quarantine_room, many=False)
            return self.response_handler.handle(data=serializer.data)
        except Exception as exception:
            return self.exception_handler.handle(exception)

    @csrf_exempt
    @action(methods=['POST'], url_path='delete', detail=False)
    def delete_quarantineroom(self, request):
        """Delete a Quarantine Room

        Args:
            + id (str)
        """

        accept_fields = [
            'id',
        ]

        require_fields = [
            'id',
        ]

        try:
            request_extractor = self.request_handler.handle(request)
            receive_fields = request_extractor.data
            accepted_fields = dict()

            for key in receive_fields:
                if key in accept_fields:
                    accepted_fields[key] = receive_fields[key]

            validator = QuarantineRoomValidator(**accepted_fields)
            validator.is_missing_fields(require_fields)
            validator.is_valid_fields(accepted_fields)

            quarantine_room = validator.get_field('id')
            quarantine_room.delete()

            serializer = BaseQuarantineRoomSerializer(quarantine_room, many=False)
            return self.response_handler.handle(data=serializer.data)
        except Exception as exception:
            return self.exception_handler.handle(exception)