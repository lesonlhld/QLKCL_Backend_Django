from rest_framework import serializers
from .models import Notification, UserNotification, CustomUser

class BaseCustomUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = ['code', 'full_name']

class NotificationSerializer(serializers.ModelSerializer):

    created_by = BaseCustomUserSerializer(many=False)
    
    class Meta:
        model = Notification
        fields = '__all__'

class NotificationSerializerForFilter(serializers.ModelSerializer):

    created_by = BaseCustomUserSerializer(many=False)
    
    class Meta:
        model = Notification
        fields = '__all__'

class UserNotificationSerializer(serializers.ModelSerializer):

    notification = NotificationSerializer(many=False)
    user = BaseCustomUserSerializer(many=False)

    class Meta:
        model = UserNotification
        fields = '__all__'

class UserNotificationSerializerForFilter(serializers.ModelSerializer):

    notification = NotificationSerializer(many=False)

    class Meta:
        model = UserNotification
        fields = ['notification', 'is_read']

class NotificationFullSerializer(serializers.ModelSerializer):

    created_by = BaseCustomUserSerializer(many=False)
    
    class Meta:
        model = Notification
        fields = '__all__'

    def to_representation(self, instance):
        data =  super().to_representation(instance)
        
        user_ids = UserNotification.objects.filter(notification__id=data['id']).values_list('user', flat=True)
        list_user = CustomUser.objects.filter(id__in=user_ids)
        data['receivers'] = BaseCustomUserSerializer(list_user, many=True).data

        return data