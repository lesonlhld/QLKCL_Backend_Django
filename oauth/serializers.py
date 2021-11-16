from rest_framework import serializers
from .models import ResetPassword
from user_account.serializers import BaseCustomUserSerializer

class ResetPasswordSerializer(serializers.ModelSerializer):

    user = BaseCustomUserSerializer(many=False)
    new_otp = serializers.CharField(source='otp')

    class Meta:
        model = ResetPassword
        fields = '__all__'