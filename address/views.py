from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework import permissions
from rest_framework.decorators import action
from .models import Country, City, District, Ward
from .serializers import (
    CountrySerializer, CitySerializer, DistrictSerializer, WardSerializer,
    BaseCitySerializer, BaseDistrictSerializer, BaseWardSerializer,
)
from .validators.country import CountryValidator
from .validators.city import CityValidator
from .validators.district import DistrictValidator
from .validators.ward import WardValidator
from .filters.city import CityFilter
from .filters.district import DistrictFilter
from .filters.ward import WardFilter
from utils import exceptions, messages
from utils.views import AbstractView, query_debugger

# Create your views here.

class CountryAPI(AbstractView):

    permission_classes = [permissions.IsAuthenticated]

    @csrf_exempt
    @action(methods=['POST'], url_path='init', detail=False)
    def init_address(self, request):
        """Init some address (country, city, district, ward)

        Args:
            None
        """

        try:
            return self.response_handler.handle(data=messages.INVALID)
            user = request.user
            if not user.role.name == 'ADMINISTRATOR':
                raise exceptions.AuthenticationException()

            try:
                vietnam = Country.objects.get(code='VNM')
            except:
                vietnam = Country(code='VNM', name='Việt Nam')
                vietnam.save()
            
            try:
                tphcm = City.objects.get(name='TP.HCM', country=vietnam)
            except:
                tphcm = City(name='TP.HCM', country=vietnam)
                tphcm.save()

            try:
                binhduong = City.objects.get(name='Bình Dương', country=vietnam)
            except:
                binhduong = City(name='Bình Dương', country=vietnam)
                binhduong.save()

            try:
                quan3 = District.objects.get(name='Quận 3', city=tphcm)
            except:
                quan3 = District(name='Quận 3', city=tphcm)
                quan3.save()

            try:
                quan7 = District.objects.get(name='Quận 7', city=tphcm)
            except:
                quan7 = District(name='Quận 7', city=tphcm)
                quan7.save()

            try:
                tpdian = District.objects.get(name='TP Dĩ An', city=binhduong)
            except:
                tpdian = District(name='TP Dĩ An', city=binhduong)
                tpdian.save()

            try:
                dautieng = District.objects.get(name='Dầu Tiếng', city=binhduong)
            except:
                dautieng = District(name='Dầu Tiếng', city=binhduong)
                dautieng.save()

            try:
                phuong4 = Ward.objects.get(name='Phường 4', district=quan3)
            except:
                phuong4 = Ward(name='Phường 4', district=quan3)
                phuong4.save()

            try:
                phumy = Ward.objects.get(name='Phú Mỹ', district=quan7)
            except:
                phumy = Ward(name='Phú Mỹ', district=quan7)
                phumy.save()

            try:
                tanbinh = Ward.objects.get(name='Tân Bình', district=tpdian)
            except:
                tanbinh = Ward(name='Tân Bình', district=tpdian)
                tanbinh.save()
            
            try:
                longhoa = Ward.objects.get(name='Long Hòa', district=dautieng)
            except:
                longhoa = Ward(name='Long Hòa', district=dautieng)
                longhoa.save()

            return self.response_handler.handle(data=messages.SUCCESS)
        except Exception as exception:
            return self.exception_handler.handle(exception)

    @csrf_exempt
    @query_debugger
    @action(methods=['GET'], url_path='get', detail=False)
    def get_country(self, request):
        """Get a Country

        Args:
            + code (str)
        """

        accept_fields = [
            'code',
        ]

        require_fields = [
            'code',
        ]

        try:
            request_extractor = self.request_handler.handle(request)
            receive_fields = request_extractor.data
            accepted_fields = dict()

            for key in receive_fields:
                if key in accept_fields:
                    accepted_fields[key] = receive_fields[key]

            validator = CountryValidator(**accepted_fields)
            validator.is_missing_fields(require_fields)
            
            if not validator.is_code_exist():
                raise exceptions.InvalidArgumentException({'code': messages.NOT_EXIST})

            country = validator.get_field('country')

            serializer = CountrySerializer(country, many=False)
            return self.response_handler.handle(data=serializer.data)
        except Exception as exception:
            return self.exception_handler.handle(exception)

    @csrf_exempt
    @query_debugger
    @action(methods=['POST'], url_path='create', detail=False)
    def create_country(self, request):
        """Create a Country

        Args:
            + code (str)
            + name (str)
        """

        accept_fields = [
            'code', 'name',
        ]

        require_fields = [
            'code', 'name',
        ]

        try:
            request_extractor = self.request_handler.handle(request)
            receive_fields = request_extractor.data
            accepted_fields = dict()

            for key in receive_fields:
                if key in accept_fields:
                    accepted_fields[key] = receive_fields[key]

            validator = CountryValidator(**accepted_fields)
            validator.is_missing_fields(require_fields)
            if validator.is_code_exist():
                raise exceptions.InvalidArgumentException({'code': messages.EXIST})

            list_to_create_country = accepted_fields.keys()
            dict_to_create_country = validator.get_data(list_to_create_country)
            country = Country(**dict_to_create_country)
            country.save()

            serializer = CountrySerializer(country, many=False)
            return self.response_handler.handle(data=serializer.data)
        except Exception as exception:
            return self.exception_handler.handle(exception)

    @csrf_exempt
    @query_debugger
    @action(methods=['POST'], url_path='update', detail=False)
    def update_country(self, request):
        """Update a Country

        Args:
            + code (str)
            - name (str)
        """

        accept_fields = [
            'code', 'name',
        ]

        require_fields = [
            'code',
        ]

        try:
            request_extractor = self.request_handler.handle(request)
            receive_fields = request_extractor.data
            accepted_fields = dict()

            for key in receive_fields:
                if key in accept_fields:
                    accepted_fields[key] = receive_fields[key]

            validator = CountryValidator(**accepted_fields)
            validator.is_missing_fields(require_fields)

            if not validator.is_code_exist():
                raise exceptions.InvalidArgumentException({'code': messages.NOT_EXIST})

            country = validator.get_field('country')

            list_to_update_country = accepted_fields.keys() - {'code'}

            dict_to_update_country = validator.get_data(list_to_update_country)

            country.__dict__.update(**dict_to_update_country)

            country.save()

            serializer = CountrySerializer(country, many=False)
            return self.response_handler.handle(data=serializer.data)
        except Exception as exception:
            return self.exception_handler.handle(exception)

    @csrf_exempt
    @query_debugger
    @action(methods=['POST'], url_path='delete', detail=False)
    def delete_country(self, request):
        """Delete a Country

        Args:
            + code (str)
        """

        accept_fields = [
            'code',
        ]

        require_fields = [
            'code',
        ]

        try:
            request_extractor = self.request_handler.handle(request)
            receive_fields = request_extractor.data
            accepted_fields = dict()

            for key in receive_fields:
                if key in accept_fields:
                    accepted_fields[key] = receive_fields[key]

            validator = CountryValidator(**accepted_fields)
            validator.is_missing_fields(require_fields)

            if not validator.is_code_exist():
                raise exceptions.InvalidArgumentException({'code': messages.NOT_EXIST})

            country = validator.get_field('country')

            country.delete()

            serializer = CountrySerializer(country, many=False)
            return self.response_handler.handle(data=serializer.data)
        except Exception as exception:
            return self.exception_handler.handle(exception)

    @csrf_exempt
    @query_debugger
    @action(methods=['POST'], url_path='filter', detail=False)
    def filter_country(self, request):
        """List all Country

        Args:
            None
        """

        try:
            list_country = Country.objects.all()

            serializer = CountrySerializer(list_country, many=True)
            return self.response_handler.handle(data=serializer.data)
        except Exception as exception:
            return self.exception_handler.handle(exception)

class CityAPI(AbstractView):
    permission_classes = [permissions.IsAuthenticated]

    @csrf_exempt
    @query_debugger
    @action(methods=['POST'], url_path='filter', detail=False)
    def filter_city(self, request):
        """List cities of country

        Args:
            + country_code: String
            - search: String
        """

        accept_fields = [
            'country_code', 'search',
        ]

        try:
            request_extractor = self.request_handler.handle(request)
            receive_fields = request_extractor.data
            accepted_fields = dict()

            for key in receive_fields.keys():
                if key in accept_fields:
                    accepted_fields[key] = receive_fields[key]

            validator = CityValidator(**accepted_fields)

            validator.is_missing_fields(['country_code',])
            validator.extra_validate_to_filter_city()

            query_set = City.objects.all()

            list_to_filter_city = [key for key in accepted_fields.keys()]

            dict_to_filter_city = validator.get_data(list_to_filter_city)

            dict_to_filter_city.setdefault('order_by', 'name')

            filter = CityFilter(dict_to_filter_city, queryset=query_set)

            query_set = filter.qs

            query_set = query_set.select_related()

            serializer = BaseCitySerializer(query_set, many=True)

            return self.response_handler.handle(data=serializer.data)
        except Exception as exception:
            return self.exception_handler.handle(exception)

class DistrictAPI(AbstractView):
    permission_classes = [permissions.IsAuthenticated]

    @csrf_exempt
    @query_debugger
    @action(methods=['POST'], url_path='filter', detail=False)
    def filter_district(self, request):
        """List districts of city

        Args:
            + city_id: int
            - search: String
        """

        accept_fields = [
            'city_id', 'search',
        ]

        try:
            request_extractor = self.request_handler.handle(request)
            receive_fields = request_extractor.data
            accepted_fields = dict()

            for key in receive_fields.keys():
                if key in accept_fields:
                    accepted_fields[key] = receive_fields[key]

            validator = DistrictValidator(**accepted_fields)

            validator.is_missing_fields(['city_id',])
            validator.extra_validate_to_filter_district()

            query_set = District.objects.all()

            list_to_filter_district = [key for key in accepted_fields.keys()]

            dict_to_filter_district = validator.get_data(list_to_filter_district)

            dict_to_filter_district.setdefault('order_by', 'name')

            filter = DistrictFilter(dict_to_filter_district, queryset=query_set)

            query_set = filter.qs

            query_set = query_set.select_related()

            serializer = BaseDistrictSerializer(query_set, many=True)

            return self.response_handler.handle(data=serializer.data)
        except Exception as exception:
            return self.exception_handler.handle(exception)

class WardAPI(AbstractView):
    permission_classes = [permissions.IsAuthenticated]

    @csrf_exempt
    @query_debugger
    @action(methods=['POST'], url_path='filter', detail=False)
    def filter_ward(self, request):
        """List wards of district

        Args:
            + district_id: int
            - search: String
        """

        accept_fields = [
            'district_id', 'search',
        ]

        try:
            request_extractor = self.request_handler.handle(request)
            receive_fields = request_extractor.data
            accepted_fields = dict()

            for key in receive_fields.keys():
                if key in accept_fields:
                    accepted_fields[key] = receive_fields[key]

            validator = WardValidator(**accepted_fields)

            validator.is_missing_fields(['district_id',])
            validator.extra_validate_to_filter_ward()

            query_set = Ward.objects.all()

            list_to_filter_ward = [key for key in accepted_fields.keys()]

            dict_to_filter_ward = validator.get_data(list_to_filter_ward)

            dict_to_filter_ward.setdefault('order_by', 'name')

            filter = WardFilter(dict_to_filter_ward, queryset=query_set)

            query_set = filter.qs

            query_set = query_set.select_related()

            serializer = BaseWardSerializer(query_set, many=True)

            return self.response_handler.handle(data=serializer.data)
        except Exception as exception:
            return self.exception_handler.handle(exception)
