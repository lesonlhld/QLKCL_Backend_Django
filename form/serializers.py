from rest_framework import serializers
from .models import MedicalDeclaration, Test
from user_account.serializers import BaseCustomUserSerializer

class MedicalDeclarationSerializer(serializers.ModelSerializer):

    user = BaseCustomUserSerializer(many=False)

    class Meta:
        model = MedicalDeclaration
        fields = '__all__'

class FilterMedicalDeclarationSerializer(serializers.ModelSerializer):

    user = BaseCustomUserSerializer(many=False)

    class Meta:
        model = MedicalDeclaration
        fields = ['id', 'user', 'created_at']

class TestSerializer(serializers.ModelSerializer):

    user = BaseCustomUserSerializer(many=False)
    created_by = BaseCustomUserSerializer(many=False)

    class Meta:
        model = Test
        fields = '__all__'

class FilterTestSerializer(serializers.ModelSerializer):

    user = BaseCustomUserSerializer(many=False)

    class Meta:
        model = Test
        fields = ['code', 'user', 'status', 'result', 'created_at', 'updated_at']
