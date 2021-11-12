from rest_framework import serializers
from .models import Country, City, District, Ward

class CountrySerializer(serializers.ModelSerializer):

    class Meta:
        model = Country
        fields = '__all__'

class BaseCountrySerializer(serializers.ModelSerializer):

    class Meta:
        model = Country
        fields = ['id', 'code', 'name']


class CitySerializer(serializers.ModelSerializer):

    class Meta:
        model = City
        fields = '__all__'

class BaseCitySerializer(serializers.ModelSerializer):

    class Meta:
        model = City
        fields = ['id', 'name']

class DistrictSerializer(serializers.ModelSerializer):

    class Meta:
        model = District
        fields = '__all__'

class BaseDistrictSerializer(serializers.ModelSerializer):

    class Meta:
        model = District
        fields = ['id', 'name']

class WardSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ward
        fields = '__all__'

class BaseWardSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ward
        fields = ['id', 'name']
