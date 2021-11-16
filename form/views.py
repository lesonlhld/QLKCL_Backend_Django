import os
import datetime
from random import randint
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from utils.views import paginate_data
from rest_framework import permissions
from rest_framework.decorators import action
from .models import BackgroundDisease, MedicalDeclaration, Symptom, Test
from .validators.medical_declaration import MedicalDeclarationValidator
from .validators.test import TestValidator
from .serializers import (
    MedicalDeclarationSerializer,
    FilterMedicalDeclarationSerializer,
    TestSerializer,
    FilterTestSerializer,
    BaseBackgroundDiseaseSerializer,
    BaseSymptomSerializer,
)
from .filters.medical_declaration import MedicalDeclarationFilter
from .filters.test import TestFilter
from utils import exceptions, messages
from utils.enums import SymptomType, TestResult, TestType
from utils.views import AbstractView

# Create your views here.

class BackgroundDiseaseAPI(AbstractView):

    permission_classes = [permissions.IsAuthenticated]

    @csrf_exempt
    @action(methods=['POST'], url_path='init', detail=False)
    def init_background_disease(self, request):
        """Init some background disease

        Args:
            None
        """

        try:
            user = request.user
            if not user.role.name == 'ADMINISTRATOR':
                raise exceptions.AuthenticationException()

            disease_list = [
                'Tiểu đường', 'Ung thư', 'Hen suyễn', 'Tăng huyết áp',
                'Bệnh gan', 'Bệnh thận mãn tính', 'Bệnh tim mạch',
                'Bệnh lý mạch máu não', 'Bệnh khác',
            ]
            
            for name in disease_list:
                try:
                    disease = BackgroundDisease.objects.get(name=name)
                except:
                    disease = BackgroundDisease(name=name)
                    disease.save()

            return self.response_handler.handle(data=messages.SUCCESS)
        except Exception as exception:
            return self.exception_handler.handle(exception)

    @csrf_exempt
    @action(methods=['POST'], url_path='filter', detail=False)
    def filter_background_disease(self, request):
        """List all background disease

        Args:
            None
        """

        try:
            serializer = BaseBackgroundDiseaseSerializer(BackgroundDisease.objects.all(), many=True)

            return self.response_handler.handle(data=serializer.data)
        except Exception as exception:
            return self.exception_handler.handle(exception)


class SymptomAPI(AbstractView):

    permission_classes = [permissions.IsAuthenticated]

    @csrf_exempt
    @action(methods=['POST'], url_path='init', detail=False)
    def init_symptom(self, request):
        """Init some symptom
        Args:
            None
        """

        try:
            user = request.user
            if not user.role.name == 'ADMINISTRATOR':
                raise exceptions.AuthenticationException()

            main_symptom_list = [
                'Ho ra máu', 'Thở dốc, khó thở', 'Đau tức ngực kéo dài', 'Lơ mơ, không tỉnh táo',
            ]

            extra_symptom_list = [
                'Mệt mỏi', 'Ho', 'Ho có đờm', 'Đau họng', 'Đau đầu', 'Chóng mặt',
                'Chán ăn', 'Nôn / Buồn nôn', 'Tiêu chảy', 'Xuất huyết ngoài da',
                'Nổi ban ngoài da', 'Ớn lạnh / gai rét', 'Viêm kết mạc (mắt đỏ)',
                'Mất vị giác, khứu giác', 'Đau nhức cơ',
            ]
            
            for name in main_symptom_list:
                try:
                    disease = Symptom.objects.get(name=name, type=SymptomType.MAIN)
                except:
                    disease = Symptom(name=name, type=SymptomType.MAIN)
                    disease.save()

            for name in extra_symptom_list:
                try:
                    disease = Symptom.objects.get(name=name, type=SymptomType.EXTRA)
                except:
                    disease = Symptom(name=name, type=SymptomType.EXTRA)
                    disease.save()

            return self.response_handler.handle(data=messages.SUCCESS)
        except Exception as exception:
            return self.exception_handler.handle(exception)

    @csrf_exempt
    @action(methods=['POST'], url_path='filter', detail=False)
    def filter_symptom(self, request):
        """List all symptom

        Args:
            None
        """

        try:
            response_data = dict()

            serializer = BaseSymptomSerializer(Symptom.objects.filter(type=SymptomType.MAIN), many=True)
            response_data['main'] = serializer.data

            serializer = BaseSymptomSerializer(Symptom.objects.filter(type=SymptomType.EXTRA), many=True)
            response_data['extra'] = serializer.data

            return self.response_handler.handle(data=response_data)
        except Exception as exception:
            return self.exception_handler.handle(exception)

class MedicalDeclarationAPI(AbstractView):

    permission_classes = [permissions.IsAuthenticated]

    @csrf_exempt
    @action(methods=['POST'], url_path='create', detail=False)
    def create_medical_declaration(self, request):
        """Create a medical declaration

        Args:
            - phone_number: String
            - heartbeat: int
            - temperature: float
            - breathing: int
            - spo2: float
            - blood_pressure: float
            - main_symptoms: String '<id>,<id>,<id>'
            - extra_symptoms: String '<id>,<id>,<id>'
            - other_symptoms: String
        """

        accept_fields = [
            'phone_number', 'heartbeat', 'temperature', 
            'breathing', 'spo2', 'blood_pressure',
            'main_symptoms', 'extra_symptoms', 'other_symptoms',
        ]

        try:
            request_extractor = self.request_handler.handle(request)
            receive_fields = request_extractor.data
            accepted_fields = dict()

            for key in receive_fields.keys():
                if key in accept_fields:
                    accepted_fields[key] = receive_fields[key]

            validator = MedicalDeclarationValidator(**accepted_fields)
            validator.is_valid_fields([
                'phone_number', 'heartbeat', 'temperature',
                'breathing', 'spo2', 'blood_pressure',
                'main_symptoms', 'extra_symptoms',
            ])
            
            validator.extra_validate_to_create_medical_declaration()

            list_to_create_medical_declaration = [key for key in accepted_fields.keys()]
            list_to_create_medical_declaration = set(list_to_create_medical_declaration) - {'phone_number'}

            dict_to_create_medical_declaration = validator.get_data(list_to_create_medical_declaration)

            medical_declaration = MedicalDeclaration(**dict_to_create_medical_declaration)
            
            for_user = request.user
            if 'phone_number' in accepted_fields.keys():
                for_user = validator.get_field('user')

            medical_declaration.user = for_user
            medical_declaration.created_by = request.user
            medical_declaration.save()

            serializer = MedicalDeclarationSerializer(medical_declaration, many=False)

            return self.response_handler.handle(data=serializer.data)
        except Exception as exception:
            return self.exception_handler.handle(exception)

    @csrf_exempt
    @action(methods=['POST'], url_path='get', detail=False)
    def get_medical_declaration(self, request):
        """Get a medical declaration

        Args:
            + id: String
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

            for key in receive_fields.keys():
                if key in accept_fields:
                    accepted_fields[key] = receive_fields[key]

            validator = MedicalDeclarationValidator(**accepted_fields)

            validator.is_missing_fields(require_fields)
            
            validator.extra_validate_to_get_medical_declaration()

            medical_declaration = validator.get_field('medical_declaration')

            serializer = MedicalDeclarationSerializer(medical_declaration, many=False)

            return self.response_handler.handle(data=serializer.data)
        except Exception as exception:
            return self.exception_handler.handle(exception)

    @csrf_exempt
    @action(methods=['POST'], url_path='filter', detail=False)
    def filter_medical_declaration(self, request):
        """Get a list of medical declarations

        Args:
            - user_code: String
            - created_at_max: String 'dd/mm/yyyy'
            - created_at_min: String 'dd/mm/yyyy'
            - page: int
            - page_size: int
            - search: String
        """

        accept_fields = [
            'user_code', 'page', 'page_size', 'search',
            'created_at_max', 'created_at_min',
        ]

        try:
            request_extractor = self.request_handler.handle(request)
            receive_fields = request_extractor.data
            accepted_fields = dict()

            for key in receive_fields.keys():
                if key in accept_fields:
                    accepted_fields[key] = receive_fields[key]

            validator = MedicalDeclarationValidator(**accepted_fields)

            validator.extra_validate_to_filter_medical_declaration()

            query_set = MedicalDeclaration.objects.all()

            list_to_filter_medical_declaration = [key for key in accepted_fields.keys()]
            list_to_filter_medical_declaration = set(list_to_filter_medical_declaration) - \
            {'page', 'page_size'}

            dict_to_filter_medical_declaration = validator.get_data(list_to_filter_medical_declaration)

            dict_to_filter_medical_declaration.setdefault('order_by', '-created_at')

            filter = MedicalDeclarationFilter(dict_to_filter_medical_declaration, queryset=query_set)

            query_set = filter.qs

            query_set = query_set.select_related()

            serializer = FilterMedicalDeclarationSerializer(query_set, many=True)

            paginated_data = paginate_data(request, serializer.data)

            return self.response_handler.handle(data=paginated_data)
        except Exception as exception:
            return self.exception_handler.handle(exception)

class TestAPI(AbstractView):
    permission_classes = [permissions.IsAuthenticated]

    def custom_test_code_generator(self, user_code):
        first_part_length = int(os.environ.get("TEST_CODE_USER_CODE_LENGTH", "3"))
        first_part = ('0000000000' + str(user_code))[-first_part_length:]
        
        second_part_length = int(os.environ.get("TEST_CODE_TIMESTAMP_LENGTH", "6"))
        second_part = ('0000000000' + str(int(datetime.datetime.now().timestamp())))[-second_part_length:]

        third_part_length = int(os.environ.get("TEST_CODE_RANDOM_LENGTH", "6"))
        third_part = ''.join(str(randint(0, 9)) for i in range(third_part_length))

        return first_part + second_part + third_part

    def update_user_after_save_test(self, test):
        if test.user != None and hasattr(test.user, 'member_x_custom_user'):
            this_member = test.user.member_x_custom_user

            if test.result == TestResult.POSITIVE:
                this_member.positive_test = True
                this_member.save()

            elif test.result == TestResult.NEGATIVE:
                if this_member.positive_test == True:
                    number_test_need = int(os.environ.get("NUMBER_TEST_FROM_POSITIVE_TO_NEGATIVE", "1"))
                elif this_member.positive_test == None:
                    number_test_need = int(os.environ.get("NUMBER_TEST_FROM_UNKNOWN_TO_NEGATIVE", "1"))

                if this_member.positive_test != False:
                    tests_to_check = Test.objects.filter(user = test.user, type=TestType.RT_PCR).order_by('-updated_at')[:number_test_need]

                    is_negative = True
                    for test in list(tests_to_check):
                        if test.result == TestResult.POSITIVE:
                            is_negative = False
                            break
                    if is_negative:
                        this_member.positive_test = False
                    else:
                        this_member.positive_test = True
                    this_member.save()

    @csrf_exempt
    @action(methods=['POST'], url_path='create', detail=False)
    def create_test(self, request):
        """Create a test

        Args:
            - user_code: String
            - status: String ['WAITING', 'DONE']
            - type: String ['QUICK', 'RT-PCR']
            - result: String ['NONE', 'NEGATIVE', 'POSITIVE']
        """

        accept_fields = [
            'user_code', 'status', 'type',
            'result',
        ]

        require_fields = [
            'user_code', 'status', 'type',
            'result',
        ]

        try:
            request_extractor = self.request_handler.handle(request)
            receive_fields = request_extractor.data
            accepted_fields = dict()

            for key in receive_fields.keys():
                if key in accept_fields:
                    accepted_fields[key] = receive_fields[key]

            validator = TestValidator(**accepted_fields)
            validator.is_missing_fields(require_fields)
            validator.is_valid_fields([
                'status', 'type', 'result',
            ])
            
            validator.extra_validate_to_create_test()

            list_to_create_test = [key for key in accepted_fields.keys()]
            list_to_create_test = set(list_to_create_test) - {'user_code'}
            list_to_create_test = list(list_to_create_test) + ['user']

            dict_to_create_test = validator.get_data(list_to_create_test)

            test = Test(**dict_to_create_test)

            test.code = self.custom_test_code_generator(test.user.code)
            while (validator.is_code_exist(test.code)):
                test.code = self.custom_test_code_generator(test.user.code)
            test.created_by = request.user
            test.save()

            # Update user
            self.update_user_after_save_test(test)

            serializer = TestSerializer(test, many=False)

            return self.response_handler.handle(data=serializer.data)
        except Exception as exception:
            return self.exception_handler.handle(exception)

    @csrf_exempt
    @action(methods=['POST'], url_path='get', detail=False)
    def get_test(self, request):
        """Get a test

        Args:
            + code: String
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

            for key in receive_fields.keys():
                if key in accept_fields:
                    accepted_fields[key] = receive_fields[key]

            validator = TestValidator(**accepted_fields)

            validator.is_missing_fields(require_fields)
            
            validator.extra_validate_to_get_test()

            test = validator.get_field('test')

            serializer = TestSerializer(test, many=False)

            return self.response_handler.handle(data=serializer.data)
        except Exception as exception:
            return self.exception_handler.handle(exception)

    @csrf_exempt
    @action(methods=['POST'], url_path='update', detail=False)
    def update_test(self, request):
        """Update a test

        Args:
            + code: String
            - status: String ['WAITING', 'DONE']
            - type: String ['QUICK', 'RT-PCR']
            - result: String ['NONE', 'NEGATIVE', 'POSITIVE']
        """

        accept_fields = [
            'code', 'status', 'type',
            'result',
        ]

        require_fields = [
            'code',
        ]

        try:
            request_extractor = self.request_handler.handle(request)
            receive_fields = request_extractor.data
            accepted_fields = dict()

            for key in receive_fields.keys():
                if key in accept_fields:
                    accepted_fields[key] = receive_fields[key]

            validator = TestValidator(**accepted_fields)
            validator.is_missing_fields(require_fields)
            validator.is_valid_fields([
                'status', 'type', 'result',
            ])
            
            validator.extra_validate_to_update_test()

            test = validator.get_field('test')

            list_to_update_test = [key for key in accepted_fields.keys()]
            list_to_update_test = set(list_to_update_test) - {'code'}

            dict_to_update_test = validator.get_data(list_to_update_test)

            for attr, value in dict_to_update_test.items(): 
                setattr(test, attr, value)

            test.updated_by = request.user
            test.save()

            # Update user
            self.update_user_after_save_test(test)

            serializer = TestSerializer(test, many=False)

            return self.response_handler.handle(data=serializer.data)
        except Exception as exception:
            return self.exception_handler.handle(exception)

    @csrf_exempt
    @action(methods=['POST'], url_path='filter', detail=False)
    def filter_test(self, request):
        """Get a list of tests

        Args:
            - user_code: String
            - status: String ['WAITING', 'DONE']
            - created_at_max: String 'dd/mm/yyyy'
            - created_at_min: String 'dd/mm/yyyy'
            - updated_at_max: String 'dd/mm/yyyy'
            - updated_at_min: String 'dd/mm/yyyy'
            - page: int
            - page_size: int
            - search: String
        """

        accept_fields = [
            'user_code', 'status',
            'created_at_max', 'created_at_min',
            'updated_at_max', 'updated_at_min',
            'page', 'page_size', 'search',
        ]

        try:
            request_extractor = self.request_handler.handle(request)
            receive_fields = request_extractor.data
            accepted_fields = dict()

            for key in receive_fields.keys():
                if key in accept_fields:
                    accepted_fields[key] = receive_fields[key]

            validator = TestValidator(**accepted_fields)

            validator.is_valid_fields(['status'])
            validator.extra_validate_to_filter_test()

            query_set = Test.objects.all()

            list_to_filter_test = [key for key in accepted_fields.keys()]
            list_to_filter_test = set(list_to_filter_test) - \
            {'page', 'page_size'}

            dict_to_filter_test = validator.get_data(list_to_filter_test)

            dict_to_filter_test.setdefault('order_by', '-created_at')

            filter = TestFilter(dict_to_filter_test, queryset=query_set)

            query_set = filter.qs

            query_set = query_set.select_related()

            serializer = FilterTestSerializer(query_set, many=True)

            paginated_data = paginate_data(request, serializer.data)

            return self.response_handler.handle(data=paginated_data)
        except Exception as exception:
            return self.exception_handler.handle(exception)
