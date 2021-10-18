from rest_framework import serializers
from .models import Country, City, District, Ward

class CountrySerializer(serializers.ModelSerializer):

    class Meta:
        model = Country
        fields = '__all__'

class CitySerializer(serializers.ModelSerializer):

    class Meta:
        model = City
        fields = '__all__'

class DistrictSerializer(serializers.ModelSerializer):

    class Meta:
        model = District
        fields = '__all__'

class WardSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ward
        fields = '__all__'