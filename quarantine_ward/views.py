from django.views.decorators.csrf import csrf_exempt
from rest_framework import permissions
from rest_framework.decorators import action, permission_classes
from utils.views import AbstractView, paginate_data
from utils import exceptions
from utils.enums import RoleName
from .models import (
    QuarantineWard,
    QuarantineBuilding,
    QuarantineFloor,
    QuarantineRoom,
)
from .serializers import (
    QuarantineWardSerializer,
    QuarantineBuildingSerializer,
    QuarantineFloorSerializer,
    QuarantineRoomSerializer,
    QuarantineWardForRegisterSerializer,
    FilterQuarantineWardSerializer,
    FilterQuarantineBuildingSerializer,
    FilterQuarantineFloorSerializer,
    FilterQuarantineRoomSerializer,
)
from .filters.quarantine_ward import QuarantineWardFilter
from .filters.quarantine_building import QuarantineBuildingFilter
from .filters.quarantine_floor import QuarantineFloorFilter
from .filters.quarantine_room import QuarantineRoomFilter
from .validators.quarantine_ward import QuarantineWardValidator
from .validators.quarantine_building import QuarantineBuildingValidator
from .validators.quarantine_floor import QuarantineFloorValidator
from .validators.quarantine_room import QuarantineRoomValidator

class QuarantineWardAPI (AbstractView):
    
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.action == 'filter_quarantineward_for_register':
            self.permission_classes = [permissions.AllowAny]
        return super().get_permissions()

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

            serializer = QuarantineWardSerializer(quarantine_ward, many=False)
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
            user = request.user
            if user.role.name != RoleName.ADMINISTRATOR:
                raise exceptions.AuthenticationException()

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

            serializer = QuarantineWardSerializer(quarantine_ward, many=False)
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
            user = request.user
            if user.role.name != RoleName.ADMINISTRATOR:
                raise exceptions.AuthenticationException()

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
            serializer = QuarantineWardSerializer(quarantine_ward, many=False)
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
            user = request.user
            if user.role.name != RoleName.ADMINISTRATOR:
                raise exceptions.AuthenticationException()

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

            serializer = QuarantineWardSerializer(quarantine_ward, many=False)
            return self.response_handler.handle(data=serializer.data)
        except Exception as exception:
            return self.exception_handler.handle(exception)
    
    @csrf_exempt
    @action(methods=['POST'], url_path='filter', detail=False)
    def filter_quarantineward(self, request):
        """Get a list of Quarantine Wards

        Args:
            - created_at_max: String 'dd/mm/yyyy'
            - created_at_min: String 'dd/mm/yyyy'
            - page: int
            - page_size: int
            - search: String
        """

        accept_fields = [
            'page', 'page_size', 'search',
            'created_at_max', 'created_at_min',
        ]

        try:
            request_extractor = self.request_handler.handle(request)
            receive_fields = request_extractor.data
            accepted_fields = dict()

            for key in receive_fields.keys():
                if key in accept_fields:
                    accepted_fields[key] = receive_fields[key]

            validator = QuarantineWardValidator(**accepted_fields)

            validator.filter_validate()

            query_set = QuarantineWard.objects.all()

            list_to_filter = [key for key in accepted_fields.keys()]
            list_to_filter = set(list_to_filter) - {'page', 'page_size'}

            dict_to_filter = validator.get_data(list_to_filter)

            dict_to_filter.setdefault('order_by', '-created_at')

            filter = QuarantineWardFilter(dict_to_filter, queryset=query_set)

            query_set = filter.qs

            query_set = query_set.select_related()

            serializer = FilterQuarantineWardSerializer(query_set, many=True)

            paginated_data = paginate_data(request, serializer.data)

            return self.response_handler.handle(data=paginated_data)
        except Exception as exception:
            return self.exception_handler.handle(exception)
    
    @csrf_exempt
    @action(methods=['POST'], url_path='filter_register', detail=False)
    def filter_quarantineward_for_register(self, request):
        """Get a list of active quarantine wards

        Args:
            None
        """

        try:
            list_quarantine_ward = QuarantineWard.objects.filter(trash=False)
            serializer = QuarantineWardForRegisterSerializer(list_quarantine_ward, many=True)

            return self.response_handler.handle(data=serializer.data)
        except Exception as exception:
            return self.exception_handler.handle(exception)
    
class QuarantineBuildingAPI (AbstractView):
    
    permission_classes = [permissions.IsAuthenticated]

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

            serializer = QuarantineBuildingSerializer(quarantine_building, many=False)
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
            user = request.user
            if user.role.name != RoleName.ADMINISTRATOR:
                raise exceptions.AuthenticationException()
                
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

            serializer = QuarantineBuildingSerializer(quarantine_building, many=False)
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
            user = request.user
            if user.role.name != RoleName.ADMINISTRATOR:
                raise exceptions.AuthenticationException()

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

            serializer = QuarantineBuildingSerializer(quarantine_building, many=False)
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
            user = request.user
            if user.role.name != RoleName.ADMINISTRATOR:
                raise exceptions.AuthenticationException()

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

            serializer = QuarantineBuildingSerializer(quarantine_building, many=False)
            return self.response_handler.handle(data=serializer.data)
        except Exception as exception:
            return self.exception_handler.handle(exception)

    @csrf_exempt
    @action(methods=['POST'], url_path='filter', detail=False)
    def filter_quarantinebuilding(self, request):
        """Get a list of Quarantine Buildings

        Args:
            - created_at_max: String 'dd/mm/yyyy'
            - created_at_min: String 'dd/mm/yyyy'
            - page: int
            - page_size: int
            - search: String
            - quarantine_ward: int (id)
        """

        accept_fields = [
            'page', 'page_size', 'search',
            'created_at_max', 'created_at_min',
            'quarantine_ward',
        ]

        required_fields = [
            'quarantine_ward'
        ]

        try:
            request_extractor = self.request_handler.handle(request)
            receive_fields = request_extractor.data
            accepted_fields = dict()

            for key in receive_fields.keys():
                if key in accept_fields:
                    accepted_fields[key] = receive_fields[key]

            validator = QuarantineBuildingValidator(**accepted_fields)
            validator.is_missing_fields(required_fields)
            validator.filter_validate()

            query_set = QuarantineBuilding.objects.all()

            list_to_filter = [key for key in accepted_fields.keys()]
            list_to_filter = set(list_to_filter) - {'page', 'page_size'}

            dict_to_filter = validator.get_data(list_to_filter)
            
            dict_to_filter.setdefault('order_by', '-created_at')
            
            filter = QuarantineBuildingFilter(dict_to_filter, queryset=query_set)

            query_set = filter.qs

            query_set = query_set.select_related()

            serializer = FilterQuarantineBuildingSerializer(query_set, many=True)

            paginated_data = paginate_data(request, serializer.data)

            return self.response_handler.handle(data=paginated_data)
        except Exception as exception:
            return self.exception_handler.handle(exception)

class QuarantineFloorAPI (AbstractView):
    
    permission_classes = [permissions.IsAuthenticated]

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

            serializer = QuarantineFloorSerializer(quarantine_floor, many=False)
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
            user = request.user
            if user.role.name != RoleName.ADMINISTRATOR:
                raise exceptions.AuthenticationException()

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

            serializer = QuarantineFloorSerializer(quarantine_floor, many=False)
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
            user = request.user
            if user.role.name != RoleName.ADMINISTRATOR:
                raise exceptions.AuthenticationException()

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

            serializer = QuarantineFloorSerializer(quarantine_floor, many=False)
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
            user = request.user
            if user.role.name != RoleName.ADMINISTRATOR:
                raise exceptions.AuthenticationException()

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

            serializer = QuarantineFloorSerializer(quarantine_floor, many=False)
            return self.response_handler.handle(data=serializer.data)
        except Exception as exception:
            return self.exception_handler.handle(exception)
    
    @csrf_exempt
    @action(methods=['POST'], url_path='filter', detail=False)
    def filter_quarantinefloor(self, request):
        """Get a list of Quarantine Floors

        Args:
            - page: int
            - page_size: int
            - search: String
            - quarantine_building: int (id)
        """

        accept_fields = [
            'page', 'page_size', 'search',
            'quarantine_building',
        ]

        required_fields = [
            'quarantine_building',
        ]

        try:
            request_extractor = self.request_handler.handle(request)
            receive_fields = request_extractor.data
            accepted_fields = dict()

            for key in receive_fields.keys():
                if key in accept_fields:
                    accepted_fields[key] = receive_fields[key]

            validator = QuarantineFloorValidator(**accepted_fields)
            validator.is_missing_fields(required_fields)
            validator.filter_validate()

            query_set = QuarantineFloor.objects.all()

            list_to_filter = [key for key in accepted_fields.keys()]
            list_to_filter = set(list_to_filter) - {'page', 'page_size'}

            dict_to_filter = validator.get_data(list_to_filter)

            dict_to_filter.setdefault('order_by', '-created_at')

            filter = QuarantineFloorFilter(dict_to_filter, queryset=query_set)

            query_set = filter.qs

            query_set = query_set.select_related()

            serializer = FilterQuarantineFloorSerializer(query_set, many=True)

            paginated_data = paginate_data(request, serializer.data)

            return self.response_handler.handle(data=paginated_data)
        except Exception as exception:
            return self.exception_handler.handle(exception)

class QuarantineRoomAPI(AbstractView):
    
    permission_classes = [permissions.IsAuthenticated]
    
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

            serializer = QuarantineRoomSerializer(quarantine_room, many=False)
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
            user = request.user
            if user.role.name != RoleName.ADMINISTRATOR:
                raise exceptions.AuthenticationException()

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

            serializer = QuarantineRoomSerializer(quarantine_room, many=False)
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
            user = request.user
            if user.role.name != RoleName.ADMINISTRATOR:
                raise exceptions.AuthenticationException()

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

            serializer = QuarantineRoomSerializer(quarantine_room, many=False)
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
            user = request.user
            if user.role.name != RoleName.ADMINISTRATOR:
                raise exceptions.AuthenticationException()

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

            serializer = QuarantineRoomSerializer(quarantine_room, many=False)
            return self.response_handler.handle(data=serializer.data)
        except Exception as exception:
            return self.exception_handler.handle(exception)
    
    @csrf_exempt
    @action(methods=['POST'], url_path='filter', detail=False)
    def filter_quarantineroom(self, request):
        """Get a list of Quarantine Rooms

        Args:
            - page: int
            - page_size: int
            - search: String
            - quarantine_floor: int (id)
        """

        accept_fields = [
            'page', 'page_size', 'search',
            'quarantine_floor',
        ]

        required_fields = [
            'quarantine_floor'
        ]

        try:
            request_extractor = self.request_handler.handle(request)
            receive_fields = request_extractor.data
            accepted_fields = dict()

            for key in receive_fields.keys():
                if key in accept_fields:
                    accepted_fields[key] = receive_fields[key]

            validator = QuarantineRoomValidator(**accepted_fields)
            validator.is_missing_fields(required_fields)
            validator.filter_validate()

            query_set = QuarantineRoom.objects.all()

            list_to_filter = [key for key in accepted_fields.keys()]
            list_to_filter = set(list_to_filter) - {'page', 'page_size'}

            dict_to_filter = validator.get_data(list_to_filter)

            dict_to_filter.setdefault('order_by', '-created_at')

            filter = QuarantineRoomFilter(dict_to_filter, queryset=query_set)

            query_set = filter.qs

            query_set = query_set.select_related()

            serializer = FilterQuarantineRoomSerializer(query_set, many=True)

            paginated_data = paginate_data(request, serializer.data)

            return self.response_handler.handle(data=paginated_data)
        except Exception as exception:
            return self.exception_handler.handle(exception)