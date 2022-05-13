from rest_framework import serializers
from .models import MedicalDeclaration, Test, BackgroundDisease, Symptom, Vaccine, VaccineDose, Pandemic
from user_account.serializers import BaseCustomUserSerializer, BaseBaseCustomUserSerializer

class PandemicSerializer(serializers.ModelSerializer):

    class Meta:
        model = Pandemic
        fields = '__all__'

class BaseBackgroundDiseaseSerializer(serializers.ModelSerializer):

    class Meta:
        model = BackgroundDisease
        fields = ['id', 'name',]

class BaseSymptomSerializer(serializers.ModelSerializer):

    class Meta:
        model = Symptom
        fields = ['id', 'name',]

class BaseMedicalDeclarationSerializer(serializers.ModelSerializer):

    user = BaseBaseCustomUserSerializer(many=False)

    class Meta:
        model = MedicalDeclaration
        fields = '__all__'

class MedicalDeclarationSerializer(serializers.ModelSerializer):

    user = BaseCustomUserSerializer(many=False)
    created_by = BaseBaseCustomUserSerializer(many=False)

    class Meta:
        model = MedicalDeclaration
        fields = '__all__'

class FilterMedicalDeclarationSerializer(serializers.ModelSerializer):

    user = BaseCustomUserSerializer(many=False)

    class Meta:
        model = MedicalDeclaration
        fields = ['id', 'code', 'user', 'conclude', 'created_at']

class BaseTestSerializer(serializers.ModelSerializer):

    user = BaseBaseCustomUserSerializer(many=False)

    class Meta:
        model = Test
        fields = [
            'code', 'user', 'status', 'result',
            'type',
            'created_at', 'updated_at',
        ]

class TestSerializer(serializers.ModelSerializer):

    user = BaseCustomUserSerializer(many=False)
    created_by = BaseCustomUserSerializer(many=False)
    updated_by = BaseCustomUserSerializer(many=False)

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

class VaccineSerializer(serializers.ModelSerializer):

    class Meta:
        model = Vaccine
        fields = '__all__'

class BaseVaccineDoseSerializer(serializers.ModelSerializer):

    vaccine = VaccineSerializer(many=False)
    custom_user = BaseBaseCustomUserSerializer(many=False)

    class Meta:
        model = VaccineDose
        fields = '__all__'

class VaccineDoseSerializer(serializers.ModelSerializer):

    vaccine = VaccineSerializer(many=False)
    custom_user = BaseCustomUserSerializer(many=False)

    class Meta:
        model = VaccineDose
        fields = '__all__'

class FilterVaccineDoseSerializer(serializers.ModelSerializer):

    vaccine = VaccineSerializer(many=False)
    custom_user = BaseBaseCustomUserSerializer(many=False)

    class Meta:
        model = VaccineDose
        fields = '__all__'
