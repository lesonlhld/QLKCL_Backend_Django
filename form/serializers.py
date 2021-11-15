from rest_framework import serializers
from .models import MedicalDeclaration, Test, BackgroundDisease, Symptom
from user_account.serializers import BaseCustomUserSerializer

class BaseBackgroundDiseaseSerializer(serializers.ModelSerializer):

    class Meta:
        model = BackgroundDisease
        fields = ['id', 'name',]

class BaseSymptomSerializer(serializers.ModelSerializer):

    class Meta:
        model = Symptom
        fields = ['id', 'name',]

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
        fields = [
            'code', 'user', 'status', 'result',
            'type',
            'created_at', 'updated_at',
        ]
