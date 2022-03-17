import re
import requests
import json
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import action
from rest_framework import permissions
from utils.views import AbstractView, paginate_data
from utils.enums import RoleName
from utils import exceptions
from .models import Notification, UserNotification, CustomUser
from .validators.notification import NotificationValidator
from .validators.user_notification import UserNotificationValidator
from .serializers import NotificationSerializer, UserNotificationSerializer, UserNotificationSerializerForFilter, NotificationFullSerializer
from .filters.notification import NotificationFilter
from .filters.user_notification import UserNotificationFilter

# Create your views here.

class NotificationAPI (AbstractView):
    
    permission_classes = [permissions.IsAuthenticated]

    @csrf_exempt
    @action(methods=['GET'], url_path='get', detail=False)
    def get_notification(self, request):
        """Get a Notification

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

            validator = NotificationValidator(**accepted_fields)
            validator.is_missing_fields(require_fields)
            validator.is_valid_fields(accepted_fields)

            notification = validator.get_field('id')

            serializer = NotificationSerializer(notification, many=False)
            return self.response_handler.handle(data=serializer.data)
        except Exception as exception:
            return self.exception_handler.handle(exception)

    @csrf_exempt
    @action(methods=['POST'], url_path='create', detail=False)
    def create_notification(self, request):
        """Create a Notification

        Args:
            + title (str)
            + description (str)
            - image (str)
            - url (str)
            - type (str)
        """

        accept_fields = [
            'title', 'description', 'image', 'url', 'type',
        ]

        require_fields = [
            'title', 'description',
        ]

        try:
            user = request.user

            request_extractor = self.request_handler.handle(request)
            receive_fields = request_extractor.data
            accepted_fields = dict()

            for key in receive_fields:
                if key in accept_fields:
                    accepted_fields[key] = receive_fields[key]

            validator = NotificationValidator(**accepted_fields)
            
            validator.is_missing_fields(require_fields)
            validator.is_valid_fields(accepted_fields)
            list_to_create = accepted_fields.keys()
            dict_to_create = validator.get_data(list_to_create)
            notification = Notification(**dict_to_create)
            notification.created_by = request.user
            notification.save()

            serializer = NotificationSerializer(notification, many=False)
            return self.response_handler.handle(data=serializer.data)
        except Exception as exception:
            return self.exception_handler.handle(exception)
    
    @csrf_exempt
    @action(methods=['POST'], url_path='create_all', detail=False)
    def create_notification_and_related(self, request):
        """Create a Notification and its related (UserNotification and notifications on user's device)

        Args:
            + title (str)
            + description (str)
            - image (str)
            - url (str)
            - type (str)
            + receiver_type (int): enum
                - 0: All user
                - 1: All user with QuarantineWard id
                - 2: External Users
            + quarantine_ward (id): required if type = 1
            + users (str of id): list id seperated by comma, required if type = 2
            + role (id)
        """

        accept_fields_for_notification = [
            'title', 'description', 'image', 'url', 'type',
        ]

        require_fields_for_notification = [
            'title', 'description',
        ]

        accept_fields_for_user_notification = [
            'receiver_type', 'quarantine_ward', 'users', 'role',
        ]

        require_fields_for_user_notification = [
            'type', 'role',
        ]

        header = {
            "Content-Type": "application/json; charset=utf-8",
            "Authorization": "Bearer " + settings.ONE_SIGNAL_REST_API_KEY,
        }

        payload = {
            "app_id": settings.ONE_SIGNAL_APP_ID,
            "headings": "",
            "contents": "",
        }

        try:
            user = request.user
            

            request_extractor = self.request_handler.handle(request)
            receive_fields = request_extractor.data
            accepted_fields_for_notification = dict()
            accepted_fields_for_user_notification = dict()

            for key in receive_fields:
                if key in accept_fields_for_notification:
                    accepted_fields_for_notification[key] = receive_fields[key]
                elif key in accept_fields_for_user_notification:
                    accepted_fields_for_user_notification[key] = receive_fields[key]

            validator = NotificationValidator(**accepted_fields_for_notification)
            
            validator.is_missing_fields(require_fields_for_notification)
            validator.is_valid_fields(accepted_fields_for_notification)
            list_to_create = accepted_fields_for_notification.keys()
            dict_to_create = validator.get_data(list_to_create)
            notification = Notification(**dict_to_create)
            notification.created_by = request.user
            notification.save()
            
            if 'receiver_type' in accepted_fields_for_user_notification:
                accepted_fields_for_user_notification['type'] = accepted_fields_for_user_notification.pop('receiver_type')
            validator = UserNotificationValidator(**accepted_fields_for_user_notification)
            
            validator.is_missing_fields(require_fields_for_user_notification)
            get_notification = notification
            get_type = validator.is_validate_type()
            get_role = validator.is_validate_role()

            payload["headings"] = {"en": get_notification.title}
            payload["contents"] = {"en": get_notification.description}
            if notification.image != None:
                payload["big_picture"] = notification.image
            if get_type == 0:
                if user.role.name == RoleName.MEMBER:
                    raise exceptions.AuthenticationException()
                all_users = CustomUser.objects.filter(role__id=get_role) if get_role > 0 else CustomUser.objects.all()
                list_user_notification = []
                for user_item in all_users:
                    validator.is_user_notification_exist_with_args(user_item, get_notification)
                    list_user_notification += [UserNotification(
                        notification=get_notification,
                        user=user_item,
                        created_by=user,
                    )]
                user_notification = UserNotification.objects.bulk_create(list_user_notification)

                if get_role == 0:
                    payload.update({"included_segments": ["Subscribed Users"]})
                else:
                    payload.update({
                        "filters": [
                            {"field": "tag", "key": "role", "relation": "=", "value": str(get_role)}
                        ]
                    })

            elif get_type == 1:
                if user.role.name == RoleName.MEMBER:
                    raise exceptions.AuthenticationException()
                validator.is_missing_fields(['quarantine_ward'])
                get_quarantine_ward = validator.is_validate_quarantine_ward()
                all_users = CustomUser.objects.filter(
                    quarantine_ward=get_quarantine_ward,
                    role__id=get_role
                ) if get_role > 0 else CustomUser.objects.filter(quarantine_ward=get_quarantine_ward)

                list_user_notification = []
                for user_item in all_users:
                    validator.is_user_notification_exist_with_args(user_item, get_notification)
                    list_user_notification += [UserNotification(
                        notification=get_notification,
                        user=user_item,
                        created_by=user,
                    )]
                user_notification = UserNotification.objects.bulk_create(list_user_notification)
                if get_role == 0:
                    payload.update({
                        "filters": [
                            {"field": "tag", "key": "quarantine_ward_id", "relation": "=", "value": str(get_quarantine_ward.id)}
                        ]
                    })
                else:
                    payload.update({
                        "filters": [
                            {"field": "tag", "key": "quarantine_ward_id", "relation": "=", "value": str(get_quarantine_ward.id)},
                            {"operator": "AND"},
                            {"field": "tag", "key": "role", "relation": "=", "value": str(get_role)}
                        ]
                    })

            else:
                validator.is_missing_fields(['users'])
                list_user_code = validator.is_validate_user_list()
                all_users = CustomUser.objects.filter(code__in=list_user_code)
                list_user_notification = []
                for user_item in all_users:
                    validator.is_user_notification_exist_with_args(user_item, get_notification)
                    list_user_notification += [UserNotification(
                        notification=get_notification,
                        user=user_item,
                        created_by=user,
                    )]
                user_notification = UserNotification.objects.bulk_create(list_user_notification)

                payload.update(
                    {
                        "include_external_user_ids": list_user_code,
                        "channel_for_external_user_ids": "push",
                    }
                )

            req = requests.post(settings.ONE_SIGNAL_NOTIFICATION_URL, headers=header, data=json.dumps(payload))

            serializer = NotificationFullSerializer(notification, many=False)
            return self.response_handler.handle(data=serializer.data)

        except Exception as exception:
            return self.exception_handler.handle(exception)
    
    @csrf_exempt
    @action(methods=['POST'], url_path='update', detail=False)
    def update_notification(self, request):
        """Update a Notification

        Args:
            + id (str)
            - title (str)
            - description (str)
            - image (str)
            - url (str)
            - type (str)
        """

        accept_fields = [
            'id', 'title', 'description', 'image', 'url', 'type',
        ]

        require_fields = [
            'id',
        ]

        try:
            user = request.user

            request_extractor = self.request_handler.handle(request)
            receive_fields = request_extractor.data
            accepted_fields = dict()

            for key in receive_fields:
                if key in accept_fields:
                    accepted_fields[key] = receive_fields[key]

            validator = NotificationValidator(**accepted_fields)
            validator.is_missing_fields(require_fields)
            validator.is_valid_fields(accepted_fields)
            notification = validator.get_field('id')
            list_to_update = accepted_fields.keys() - {'id'}
            
            dict_to_update = validator.get_data(list_to_update)
            notification.__dict__.update(**dict_to_update)
            notification.save()
            serializer = NotificationSerializer(notification, many=False)
            return self.response_handler.handle(data=serializer.data)
        except Exception as exception:
            return self.exception_handler.handle(exception)

    @csrf_exempt
    @action(methods=['POST'], url_path='delete', detail=False)
    def delete_notification(self, request):
        """Delete a Notification

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

            request_extractor = self.request_handler.handle(request)
            receive_fields = request_extractor.data
            accepted_fields = dict()

            for key in receive_fields:
                if key in accept_fields:
                    accepted_fields[key] = receive_fields[key]

            validator = NotificationValidator(**accepted_fields)
            validator.is_missing_fields(require_fields)
            validator.is_valid_fields(accepted_fields)

            notification = validator.get_field('id')
            notification.delete()

            serializer = NotificationSerializer(notification, many=False)
            return self.response_handler.handle(data=serializer.data)
        except Exception as exception:
            return self.exception_handler.handle(exception)
    
    @csrf_exempt
    @action(methods=['POST'], url_path='filter', detail=False)
    def filter_notification(self, request):
        """Get a list of Notifications

        Args:
            - created_at_max: String vd:'2000-01-26T01:23:45.123456Z'
            - created_at_min: String vd:'2000-01-26T01:23:45.123456Z'
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

            validator = NotificationValidator(**accepted_fields)
            validator.is_valid_fields([
                'created_at_max', 'created_at_min',
            ])

            query_set = Notification.objects.all()

            list_to_filter = [key for key in accepted_fields.keys()]
            list_to_filter = set(list_to_filter) - {'page', 'page_size'}

            dict_to_filter = validator.get_data(list_to_filter)

            dict_to_filter.setdefault('order_by', '-created_at')

            filter = NotificationFilter(dict_to_filter, queryset=query_set)

            query_set = filter.qs

            query_set = query_set.select_related()

            serializer = NotificationSerializer(query_set, many=True)

            paginated_data = paginate_data(request, serializer.data)

            return self.response_handler.handle(data=paginated_data)
        except Exception as exception:
            return self.exception_handler.handle(exception)

class UserNotificationAPI (AbstractView):
    
    permission_classes = [permissions.IsAuthenticated]

    @csrf_exempt
    @action(methods=['GET'], url_path='get', detail=False)
    def get_user_notification(self, request):
        """Get a User Notification

        Args:
            - user (int): id
            + notification (int): id
        """

        accept_fields = [
            'user', 'notification'
        ]

        require_fields = [
            'notification'
        ]

        try:
            user = request.user
            request_extractor = self.request_handler.handle(request)
            receive_fields = request_extractor.data
            accepted_fields = dict()

            for key in receive_fields:
                if key in accept_fields:
                    accepted_fields[key] = receive_fields[key]

            if 'user' not in accepted_fields:
                accepted_fields['user'] = user.id

            validator = UserNotificationValidator(**accepted_fields)
            validator.is_missing_fields(require_fields)
            validator.is_valid_fields(accepted_fields)
            user_notification = validator.is_user_notification_exist()

            serializer = UserNotificationSerializer(user_notification, many=False)
            return self.response_handler.handle(data=serializer.data)
        except Exception as exception:
            return self.exception_handler.handle(exception)

    @csrf_exempt
    @action(methods=['POST'], url_path='create', detail=False)
    def create_user_notification(self, request):
        """Create a UserNotification and send Notification to user account

        Args:
            + notification (id)
            + type (int): enum
                - 0: All user
                - 1: All user with QuarantineWard id
                - 2: External Users
            + quarantine_ward (id): required if type = 1
            + users (str of id): list id seperated by comma, required if type = 2
            + role (id)
                
        """

        accept_fields = [
            'notification', 'type', 'quarantine_ward', 'users', 'role',
        ]

        require_fields = [
            'notification', 'type', 'role',
        ]

        header = {
            "Content-Type": "application/json; charset=utf-8",
            "Authorization": "Bearer " + settings.ONE_SIGNAL_REST_API_KEY,
        }

        payload = {
            "app_id": settings.ONE_SIGNAL_APP_ID,
            "headings": "",
            "contents": "",
        }

        try:
            user = request.user

            request_extractor = self.request_handler.handle(request)
            receive_fields = request_extractor.data
            accepted_fields = dict()

            for key in receive_fields:
                if key in accept_fields:
                    accepted_fields[key] = receive_fields[key]

            validator = UserNotificationValidator(**accepted_fields)
            
            validator.is_missing_fields(require_fields)
            get_notification = validator.is_validate_notification()
            get_type = validator.is_validate_type()
            get_role = validator.is_validate_role()

            payload["headings"] = {"en": get_notification.title}
            payload["contents"] = {"en": get_notification.description}
            if get_notification.image != None:
                payload["big_picture"] = get_notification.image
            if get_type == 0:
                if user.role.name == RoleName.MEMBER:
                    raise exceptions.AuthenticationException()
                all_users = CustomUser.objects.filter(role__id=get_role) if get_role > 0 else CustomUser.objects.all()
                list_user_notification = []
                for user_item in all_users:
                    validator.is_user_notification_exist_with_args(user_item, get_notification)
                    list_user_notification += [UserNotification(
                        notification=get_notification,
                        user=user_item,
                        created_by=user,
                    )]
                user_notification = UserNotification.objects.bulk_create(list_user_notification)
                serializer = UserNotificationSerializer(user_notification, many=True)
                if get_role == 0:
                    payload.update({"included_segments": ["Subscribed Users"]})
                else:
                    payload.update({
                        "filters": [
                            {"field": "tag", "key": "role", "relation": "=", "value": str(get_role)}
                        ]
                    })

            elif get_type == 1:
                if user.role.name == RoleName.MEMBER:
                    raise exceptions.AuthenticationException()
                validator.is_missing_fields(['quarantine_ward'])
                get_quarantine_ward = validator.is_validate_quarantine_ward()
                all_users = CustomUser.objects.filter(
                    quarantine_ward=get_quarantine_ward,
                    role__id=get_role
                ) if get_role > 0 else CustomUser.objects.filter(quarantine_ward=get_quarantine_ward)

                list_user_notification = []
                for user_item in all_users:
                    validator.is_user_notification_exist_with_args(user_item, get_notification)
                    list_user_notification += [UserNotification(
                        notification=get_notification,
                        user=user_item,
                        created_by=user,
                    )]
                user_notification = UserNotification.objects.bulk_create(list_user_notification)
                serializer = UserNotificationSerializer(user_notification, many=True)
                if get_role == 0:
                    payload.update({
                        "filters": [
                            {"field": "tag", "key": "quarantine_ward_id", "relation": "=", "value": str(get_quarantine_ward.id)}
                        ]
                    })
                else:
                    payload.update({
                        "filters": [
                            {"field": "tag", "key": "quarantine_ward_id", "relation": "=", "value": str(get_quarantine_ward.id)},
                            {"operator": "AND"},
                            {"field": "tag", "key": "role", "relation": "=", "value": str(get_role)}
                        ]
                    })

            else:
                validator.is_missing_fields(['users'])
                list_user_code = validator.is_validate_user_list()
                all_users = CustomUser.objects.filter(code__in=list_user_code)
                list_user_notification = []
                for user_item in all_users:
                    validator.is_user_notification_exist_with_args(user_item, get_notification)
                    list_user_notification += [UserNotification(
                        notification=get_notification,
                        user=user_item,
                        created_by=user,
                    )]
                user_notification = UserNotification.objects.bulk_create(list_user_notification)
                serializer = UserNotificationSerializer(user_notification, many=True)

                payload.update(
                    {
                        "include_external_user_ids": list_user_code,
                        "channel_for_external_user_ids": "push",
                    }
                )

            req = requests.post(settings.ONE_SIGNAL_NOTIFICATION_URL, headers=header, data=json.dumps(payload))
            
            return self.response_handler.handle(data=serializer.data)
        except Exception as exception:
            return self.exception_handler.handle(exception)
    
    @csrf_exempt
    @action(methods=['POST'], url_path='change_status', detail=False)
    def change_read_status_user_notification(self, request):
        """Change is_read field in UserNotification 

        Args:
            + notification (id)
        """

        accept_fields = [
            'notification'
        ]

        require_fields = [
            'notification'
        ]

        try:
            user = request.user

            request_extractor = self.request_handler.handle(request)
            receive_fields = request_extractor.data
            accepted_fields = dict()

            for key in receive_fields:
                if key in accept_fields:
                    accepted_fields[key] = receive_fields[key]
            
            accepted_fields['user'] = user.id

            validator = UserNotificationValidator(**accepted_fields)
            validator.is_missing_fields(require_fields)
            validator.is_valid_fields(accepted_fields)
            user_notification = validator.is_user_notification_exist()
            user_notification.is_read = not user_notification.is_read
            user_notification.save()
            serializer = UserNotificationSerializer(user_notification, many=False)
            return self.response_handler.handle(data=serializer.data)
        except Exception as exception:
            return self.exception_handler.handle(exception)

    @csrf_exempt
    @action(methods=['POST'], url_path='delete', detail=False)
    def delete_user_notification(self, request):
        """Delete a UserNotification

        Args:
            - user (id)
            + notification_list (list of id seperated by comma)
        """

        accept_fields = [
            'user', 'notification_list'
        ]

        require_fields = [
            'notification_list'
        ]

        try:
            user = request.user

            request_extractor = self.request_handler.handle(request)
            receive_fields = request_extractor.data
            accepted_fields = dict()

            for key in receive_fields:
                if key in accept_fields:
                    accepted_fields[key] = receive_fields[key]

            if 'user' not in accepted_fields:
                accepted_fields['user'] = user.id

            validator = UserNotificationValidator(**accepted_fields)
            validator.is_missing_fields(require_fields)
            list_notification = validator.is_validate_notification_list()
            get_user = validator.is_validate_user()
            list_user_notification_id = validator.is_user_notification_exist_with_args_list(get_user, list_notification)
            list_user_notification = UserNotification.objects.filter(id__in=list_user_notification_id)
            list_user_notification.delete()
            serializer = UserNotificationSerializer(list_user_notification, many=True)

            return self.response_handler.handle(data=serializer.data)
        except Exception as exception:
            return self.exception_handler.handle(exception)

    @csrf_exempt
    @action(methods=['POST'], url_path='filter', detail=False)
    def filter_user_notification(self, request):
        """Get a list of Notifications of a User

        Args:
            - created_at_max: String vd:'2000-01-26T01:23:45.123456Z'
            - created_at_min: String vd:'2000-01-26T01:23:45.123456Z'
            - page: int
            - page_size: int
            - user (id)
        """

        accept_fields = [
            'page', 'page_size', 'user',
            'created_at_max', 'created_at_min',
        ]

        try:
            user = request.user
            request_extractor = self.request_handler.handle(request)
            receive_fields = request_extractor.data
            accepted_fields = dict()

            for key in receive_fields.keys():
                if key in accept_fields:
                    accepted_fields[key] = receive_fields[key]

            validator = UserNotificationValidator(**accepted_fields)
            validator.is_valid_fields(accepted_fields)
            if validator.has_field('user'):
                user = validator.get_field('user')
            query_set = UserNotification.objects.filter(user=user)

            list_to_filter = [key for key in accepted_fields.keys()]
            list_to_filter = set(list_to_filter) - {'page', 'page_size'}

            dict_to_filter = validator.get_data(list_to_filter)

            dict_to_filter.setdefault('order_by', '-created_at')

            filter = UserNotificationFilter(dict_to_filter, queryset=query_set)

            query_set = filter.qs

            query_set = query_set.select_related()

            serializer = UserNotificationSerializerForFilter(query_set, many=True)

            paginated_data = paginate_data(request, serializer.data)

            return self.response_handler.handle(data=paginated_data)
        except Exception as exception:
            return self.exception_handler.handle(exception)
    