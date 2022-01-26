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

class UserNotificationSerializer(serializers.ModelSerializer):

    notification = NotificationSerializer(many=False)
    user = BaseCustomUserSerializer(many=False)

    class Meta:
        model = UserNotification
        fields = '__all__'