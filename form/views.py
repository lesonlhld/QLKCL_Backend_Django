import os
import datetime
from random import randint
from django.db.models import Q
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from utils.views import paginate_data
from rest_framework import permissions
from rest_framework.decorators import action
from .models import BackgroundDisease, MedicalDeclaration, Symptom, Test, Vaccine, VaccineDose
from .validators.medical_declaration import MedicalDeclarationValidator
from .validators.test import TestValidator
from .validators.vaccine import VaccineValidator, VaccineDoseValidator
from .serializers import (
    MedicalDeclarationSerializer,
    FilterMedicalDeclarationSerializer,
    TestSerializer,
    FilterTestSerializer,
    BaseBackgroundDiseaseSerializer,
    BaseSymptomSerializer,
    VaccineSerializer,
    VaccineDoseSerializer,
    FilterVaccineDoseSerializer,
)
from .filters.medical_declaration import MedicalDeclarationFilter
from .filters.test import TestFilter
from .filters.vaccine import VaccineDoseFilter
from utils import exceptions, messages
from utils.enums import SymptomType, TestResult, TestType, HealthStatus, MemberLabel
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

    def custom_medical_declaration_code_generator(self, user_code):
        first_part_length = int(os.environ.get("MEDICAL_DECLARATION_CODE_USER_CODE_LENGTH", "3"))
        first_part = ('0000000000' + str(user_code))[-first_part_length:]
        
        second_part_length = int(os.environ.get("MEDICAL_DECLARATION_CODE_TIMESTAMP_LENGTH", "6"))
        second_part = ('0000000000' + str(int(datetime.datetime.now().timestamp())))[-second_part_length:]

        third_part_length = int(os.environ.get("MEDICAL_DECLARATION_CODE_RANDOM_LENGTH", "6"))
        third_part = ''.join(str(randint(0, 9)) for i in range(third_part_length))

        return first_part + second_part + third_part

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
            list_to_create_medical_declaration = list(list_to_create_medical_declaration) + ['conclude']

            dict_to_create_medical_declaration = validator.get_data(list_to_create_medical_declaration)

            medical_declaration = MedicalDeclaration(**dict_to_create_medical_declaration)
            
            for_user = request.user
            if 'phone_number' in accepted_fields.keys():
                for_user = validator.get_field('user')

            medical_declaration.user = for_user

            medical_declaration.code = self.custom_medical_declaration_code_generator(medical_declaration.user.code)
            while (validator.is_code_exist(medical_declaration.code)):
                medical_declaration.code = self.custom_medical_declaration_code_generator(medical_declaration.user.code)

            medical_declaration.created_by = request.user
            medical_declaration.save()

            if hasattr(for_user, 'member_x_custom_user'):
                for_member = for_user.member_x_custom_user
                for_member.health_status = medical_declaration.conclude
                for_member.save()

            if hasattr(for_user, 'manager_x_custom_user'):
                for_manager = for_user.manager_x_custom_user
                for_manager.health_status = medical_declaration.conclude
                for_manager.save()
            
            if hasattr(for_user, 'staff_x_custom_user'):
                for_staff = for_user.staff_x_custom_user
                for_staff.health_status = medical_declaration.conclude
                for_staff.save()

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
            - created_at_max: String vd:'2000-01-26T01:23:45.123456Z'
            - created_at_min: String vd:'2000-01-26T01:23:45.123456Z'
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

            validator.is_valid_fields([
                'created_at_max', 'created_at_min',
            ])
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

    def calculate_new_conclude_from_test(self, test, old_positive_test_now):
        """test must be the last test has result of this member"""
        if test.result == TestResult.POSITIVE:
            return True
        elif test.result == TestResult.NEGATIVE:
            if old_positive_test_now == False or old_positive_test_now == None:
                return False
            else:
                number_test_need = int(os.environ.get("NUMBER_TEST_FROM_POSITIVE_TO_NEGATIVE", "3"))
                tests_to_check = Test.objects.filter(user = test.user, type=TestType.RT_PCR).filter(~Q(result=TestResult.NONE)).order_by('-created_at')[:number_test_need]
                tests_to_check = list(tests_to_check)
                if len(tests_to_check) < number_test_need:
                    return True
                is_positive = False
                for test in tests_to_check:
                    if test.result == TestResult.POSITIVE:
                        is_positive = True
                        break
                return is_positive
        else:
            return old_positive_test_now

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
            user = test.user
            if hasattr(user, 'member_x_custom_user'):
                this_member = user.member_x_custom_user
                this_member.last_tested = test.created_at

                if test.result != TestResult.NONE:
                    old_positive_test_now = this_member.positive_test_now
                    new_positive_test_now = self.calculate_new_conclude_from_test(test, old_positive_test_now)
                    this_member.positive_test_now = new_positive_test_now

                    if old_positive_test_now != True and new_positive_test_now == True:
                        this_member.label = MemberLabel.F0
                        this_room = this_member.quarantine_room
                        members_in_this_room = this_room.member_x_quarantine_room.all()
                        for member in list(members_in_this_room):
                            if member.label != MemberLabel.F0:
                                member.label = MemberLabel.F1
                                member.quarantined_finish_expected_at = None
                                member.save()
                    elif old_positive_test_now == True and new_positive_test_now == False:
                        this_room = this_member.quarantine_room
                        members_in_this_room = this_room.member_x_quarantine_room.all()
                        for member in list(members_in_this_room):
                            if member.label != MemberLabel.F0:
                                number_of_quarantine_days = int(member.custom_user.quarantine_ward.quarantine_time)
                                member.quarantined_finish_expected_at = timezone.now() + datetime.timedelta(days=number_of_quarantine_days)
                                member.save()

                    this_member.last_tested_had_result = test.created_at
                this_member.save()
            if hasattr(user, 'manager_x_custom_user'):
                this_manager = user.manager_x_custom_user
                this_manager.last_tested = test.created_at
                if test.result != TestResult.NONE:
                    new_positive_test_now = self.calculate_new_conclude_from_test(test, this_manager.positive_test_now)
                    this_manager.positive_test_now = new_positive_test_now
                    this_manager.last_tested_had_result = test.created_at
                this_manager.save()
            if hasattr(user, 'staff_x_custom_user'):
                this_staff = user.staff_x_custom_user
                this_staff.last_tested = test.created_at
                if test.result != TestResult.NONE:
                    new_positive_test_now = self.calculate_new_conclude_from_test(test, this_staff.positive_test_now)
                    this_staff.positive_test_now = new_positive_test_now
                    this_staff.last_tested_had_result = test.created_at
                this_staff.save()

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
            if test.result != TestResult.NONE:
                # if this test has result
                last_test_has_result = Test.objects.filter(user = test.user).filter(~Q(result=TestResult.NONE)).order_by('-created_at')[0]
                if last_test_has_result == test:
                    # if this test is the last test of this user that has result
                    if hasattr(test.user, 'member_x_custom_user'):
                        this_member = test.user.member_x_custom_user
                        old_positive_test_now = this_member.positive_test_now
                        new_positive_test_now = self.calculate_new_conclude_from_test(test, this_member.positive_test_now)
                        this_member.positive_test_now = new_positive_test_now

                        if old_positive_test_now != True and new_positive_test_now == True:
                            this_member.label = MemberLabel.F0
                            this_room = this_member.quarantine_room
                            members_in_this_room = this_room.member_x_quarantine_room.all()
                            for member in list(members_in_this_room):
                                if member.label != MemberLabel.F0:
                                    member.label = MemberLabel.F1
                                    member.quarantined_finish_expected_at = None
                                    member.save()
                        elif old_positive_test_now == True and new_positive_test_now == False:
                            this_room = this_member.quarantine_room
                            members_in_this_room = this_room.member_x_quarantine_room.all()
                            for member in list(members_in_this_room):
                                if member.label != MemberLabel.F0:
                                    number_of_quarantine_days = int(member.custom_user.quarantine_ward.quarantine_time)
                                    member.quarantined_finish_expected_at = timezone.now() + datetime.timedelta(days=number_of_quarantine_days)
                                    member.save()

                        this_member.last_tested_had_result = test.created_at
                        this_member.save()

                    if hasattr(test.user, 'manager_x_custom_user'):
                        this_manager = test.user.manager_x_custom_user
                        new_positive_test_now = self.calculate_new_conclude_from_test(test, this_manager.positive_test_now)
                        this_manager.positive_test_now = new_positive_test_now
                        this_manager.last_tested_had_result = test.created_at
                        this_manager.save()
                        
                    if hasattr(test.user, 'staff_x_custom_user'):
                        this_staff = test.user.staff_x_custom_user
                        new_positive_test_now = self.calculate_new_conclude_from_test(test, this_staff.positive_test_now)
                        this_staff.positive_test_now = new_positive_test_now
                        this_staff.last_tested_had_result = test.created_at
                        this_staff.save()

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
            - result: String ['NONE', 'NEGATIVE', 'POSITIVE']
            - type: String ['QUICK', 'RT-PCR']
            - created_at_max: String vd:'2000-01-26T01:23:45.123456Z'
            - created_at_min: String vd:'2000-01-26T01:23:45.123456Z'
            - updated_at_max: String vd:'2000-01-26T01:23:45.123456Z'
            - updated_at_min: String vd:'2000-01-26T01:23:45.123456Z'
            - page: int
            - page_size: int
            - search: String
        """

        accept_fields = [
            'user_code', 'status',
            'result', 'type',
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

            validator.is_valid_fields([
                'status', 'result', 'type',
                'created_at_max', 'created_at_min',
                'updated_at_max', 'updated_at_min',
            ])
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

class VaccineAPI(AbstractView):

    permission_classes = [permissions.IsAuthenticated]

    @csrf_exempt
    @action(methods=['POST'], url_path='get', detail=False)
    def get_vaccine(self, request):
        """Get a vaccine

        Args:
            + id: int
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

            validator = VaccineValidator(**accepted_fields)

            validator.is_missing_fields(require_fields)
            
            validator.extra_validate_to_get_vaccine()

            vaccine = validator.get_field('vaccine')

            serializer = VaccineSerializer(vaccine, many=False)

            return self.response_handler.handle(data=serializer.data)
        except Exception as exception:
            return self.exception_handler.handle(exception)

    @csrf_exempt
    @action(methods=['POST'], url_path='create', detail=False)
    def create_vaccine(self, request):
        """Create a vaccine

        Args:
            + name: String
            + manufacturer: String
        """

        accept_fields = [
            'name', 'manufacturer',
        ]

        require_fields = [
            'name', 'manufacturer',
        ]

        try:
            if request.user.role.name not in ['ADMINISTRATOR', 'SUPER_MANAGER']:
                raise exceptions.AuthenticationException({'main': messages.NO_PERMISSION})

            request_extractor = self.request_handler.handle(request)
            receive_fields = request_extractor.data
            accepted_fields = dict()

            for key in receive_fields.keys():
                if key in accept_fields:
                    accepted_fields[key] = receive_fields[key]

            validator = VaccineValidator(**accepted_fields)
            validator.is_missing_fields(require_fields)
            
            validator.extra_validate_to_create_vaccine()

            list_to_create_test = [key for key in accepted_fields.keys()]

            dict_to_create_test = validator.get_data(list_to_create_test)

            vaccine = Vaccine(**dict_to_create_test)
            vaccine.save()

            serializer = VaccineSerializer(vaccine, many=False)
            
            return self.response_handler.handle(data=serializer.data)
        except Exception as exception:
            return self.exception_handler.handle(exception)

    @csrf_exempt
    @action(methods=['POST'], url_path='update', detail=False)
    def update_vaccine(self, request):
        """Update a vaccine

        Args:
            + id: int
            - name: String
            - manufacturer: String
        """

        accept_fields = [
            'id',
            'name', 'manufacturer',
        ]

        require_fields = [
            'id',
        ]

        try:
            if request.user.role.name not in ['ADMINISTRATOR', 'SUPER_MANAGER']:
                raise exceptions.AuthenticationException({'main': messages.NO_PERMISSION})

            request_extractor = self.request_handler.handle(request)
            receive_fields = request_extractor.data
            accepted_fields = dict()

            for key in receive_fields.keys():
                if key in accept_fields:
                    accepted_fields[key] = receive_fields[key]

            validator = VaccineValidator(**accepted_fields)
            validator.is_missing_fields(require_fields)
            
            validator.extra_validate_to_update_vaccine()

            vaccine = validator.get_field('vaccine')

            list_to_update_vaccine = [key for key in accepted_fields.keys()]
            list_to_update_vaccine = set(list_to_update_vaccine) - {'id'}

            dict_to_update_vaccine = validator.get_data(list_to_update_vaccine)

            for attr, value in dict_to_update_vaccine.items(): 
                setattr(vaccine, attr, value)

            vaccine.save()

            serializer = VaccineSerializer(vaccine, many=False)
            
            return self.response_handler.handle(data=serializer.data)
        except Exception as exception:
            return self.exception_handler.handle(exception)

    @csrf_exempt
    @action(methods=['POST'], url_path='filter', detail=False)
    def filter_vaccine(self, request):
        """Get a list of vaccine

        Args:
            None
        """

        try:
            query_set = Vaccine.objects.all().order_by('id')

            serializer = VaccineSerializer(query_set, many=True)

            return self.response_handler.handle(data=serializer.data)
        except Exception as exception:
            return self.exception_handler.handle(exception)

class VaccineDoseAPI(AbstractView):

    permission_classes = [permissions.IsAuthenticated]

    @csrf_exempt
    @action(methods=['POST'], url_path='get', detail=False)
    def get_vaccine_dose(self, request):
        """Get a vaccine dose

        Args:
            + id: int
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

            validator = VaccineDoseValidator(**accepted_fields)

            validator.is_missing_fields(require_fields)
            
            validator.extra_validate_to_get_vaccine_dose()

            vaccine_dose = validator.get_field('vaccine_dose')

            serializer = VaccineDoseSerializer(vaccine_dose, many=False)

            return self.response_handler.handle(data=serializer.data)
        except Exception as exception:
            return self.exception_handler.handle(exception)

    @csrf_exempt
    @action(methods=['POST'], url_path='create', detail=False)
    def create_vaccine_dose(self, request):
        """Create a vaccine dose

        Args:
            + vaccine_id: int
            + custom_user_code: String
            + injection_date: String vd:'2000-01-26T01:23:45.123456Z'
            - injection_place: String
            - batch_number: String
            - symptom_after_injected: String
        """

        accept_fields = [
            'vaccine_id', 'custom_user_code',
            'injection_date', 'injection_place',
            'batch_number', 'symptom_after_injected',
        ]

        require_fields = [
            'vaccine_id', 'custom_user_code',
            'injection_date',
        ]

        try:
            if request.user.role.name not in ['ADMINISTRATOR', 'SUPER_MANAGER', 'MANAGER', 'STAFF']:
                raise exceptions.AuthenticationException({'main': messages.NO_PERMISSION})

            request_extractor = self.request_handler.handle(request)
            receive_fields = request_extractor.data
            accepted_fields = dict()

            for key in receive_fields.keys():
                if key in accept_fields:
                    accepted_fields[key] = receive_fields[key]

            validator = VaccineDoseValidator(**accepted_fields)
            validator.is_missing_fields(require_fields)
            validator.is_valid_fields(['injection_date'])
            
            validator.extra_validate_to_create_vaccine_dose()

            list_to_create_vaccine_dose = [key for key in accepted_fields.keys()]

            list_to_create_vaccine_dose = set(list_to_create_vaccine_dose) - \
            {'vaccine_id', 'custom_user_code',}
            list_to_create_vaccine_dose = list(list_to_create_vaccine_dose) + \
            ['vaccine', 'custom_user',]

            dict_to_create_vaccine_dose = validator.get_data(list_to_create_vaccine_dose)

            vaccine_dose = VaccineDose(**dict_to_create_vaccine_dose)
            vaccine_dose.save()

            # Update member/manager/staff.number_of_vaccine_doses

            custom_user = vaccine_dose.custom_user

            if hasattr(custom_user, 'member_x_custom_user'):
                member = custom_user.member_x_custom_user
                member.number_of_vaccine_doses = VaccineDose.objects.filter(custom_user=custom_user).count()
                member.save()

            if hasattr(custom_user, 'manager_x_custom_user'):
                manager = custom_user.manager_x_custom_user
                manager.number_of_vaccine_doses = VaccineDose.objects.filter(custom_user=custom_user).count()
                manager.save()
            
            if hasattr(custom_user, 'staff_x_custom_user'):
                staff = custom_user.staff_x_custom_user
                staff.number_of_vaccine_doses = VaccineDose.objects.filter(custom_user=custom_user).count()
                staff.save()

            serializer = VaccineDoseSerializer(vaccine_dose, many=False)
            
            return self.response_handler.handle(data=serializer.data)
        except Exception as exception:
            return self.exception_handler.handle(exception)

    @csrf_exempt
    @action(methods=['POST'], url_path='update', detail=False)
    def update_vaccine_dose(self, request):
        """Update a vaccine dose

        Args:
            + id: int
            - vaccine_id: int
            - injection_date: String vd:'2000-01-26T01:23:45.123456Z'
            - injection_place: String
            - batch_number: String
            - symptom_after_injected: String
        """

        accept_fields = [
            'id', 'vaccine_id',
            'injection_date', 'injection_place',
            'batch_number', 'symptom_after_injected',
        ]

        require_fields = [
            'id',
        ]

        try:
            if request.user.role.name not in ['ADMINISTRATOR', 'SUPER_MANAGER', 'MANAGER', 'STAFF']:
                raise exceptions.AuthenticationException({'main': messages.NO_PERMISSION})

            request_extractor = self.request_handler.handle(request)
            receive_fields = request_extractor.data
            accepted_fields = dict()

            for key in receive_fields.keys():
                if key in accept_fields:
                    accepted_fields[key] = receive_fields[key]

            validator = VaccineDoseValidator(**accepted_fields)
            validator.is_missing_fields(require_fields)
            validator.is_valid_fields(['injection_date'])
            
            validator.extra_validate_to_update_vaccine_dose()

            vaccine_dose = validator.get_field('vaccine_dose')

            list_to_update_vaccine_dose = [key for key in accepted_fields.keys()]
            list_to_update_vaccine_dose = set(list_to_update_vaccine_dose) - \
            {'id', 'vaccine_id'}
            list_to_update_vaccine_dose = list(list_to_update_vaccine_dose) + \
            ['vaccine']

            dict_to_update_vaccine_dose = validator.get_data(list_to_update_vaccine_dose)

            for attr, value in dict_to_update_vaccine_dose.items(): 
                setattr(vaccine_dose, attr, value)

            vaccine_dose.save()

            serializer = VaccineDoseSerializer(vaccine_dose, many=False)
            
            return self.response_handler.handle(data=serializer.data)
        except Exception as exception:
            return self.exception_handler.handle(exception)

    @csrf_exempt
    @action(methods=['POST'], url_path='delete', detail=False)
    def delete_vaccine_dose(self, request):
        """Delete a vaccine dose

        Args:
            + id: int
        """

        accept_fields = [
            'id'
        ]

        require_fields = [
            'id'
        ]

        try:
            if request.user.role.name not in ['ADMINISTRATOR', 'SUPER_MANAGER', 'MANAGER', 'STAFF']:
                raise exceptions.AuthenticationException({'main': messages.NO_PERMISSION})

            request_extractor = self.request_handler.handle(request)
            receive_fields = request_extractor.data
            accepted_fields = dict()

            for key in receive_fields.keys():
                if key in accept_fields:
                    accepted_fields[key] = receive_fields[key]

            validator = VaccineDoseValidator(**accepted_fields)
            validator.is_missing_fields(require_fields)
            
            validator.extra_validate_to_delete_vaccine_dose()

            vaccine_dose = validator.get_field('vaccine_dose')

            custom_user = vaccine_dose.custom_user

            vaccine_dose.delete()

            # Update member/manager/staff.number_of_vaccine_doses

            if hasattr(custom_user, 'member_x_custom_user'):
                member = custom_user.member_x_custom_user
                member.number_of_vaccine_doses = VaccineDose.objects.filter(custom_user=custom_user).count()
                member.save()

            if hasattr(custom_user, 'manager_x_custom_user'):
                manager = custom_user.manager_x_custom_user
                manager.number_of_vaccine_doses = VaccineDose.objects.filter(custom_user=custom_user).count()
                manager.save()
            
            if hasattr(custom_user, 'staff_x_custom_user'):
                staff = custom_user.staff_x_custom_user
                staff.number_of_vaccine_doses = VaccineDose.objects.filter(custom_user=custom_user).count()
                staff.save()
            
            return self.response_handler.handle(data=messages.SUCCESS)
        except Exception as exception:
            return self.exception_handler.handle(exception)

    @csrf_exempt
    @action(methods=['POST'], url_path='filter', detail=False)
    def filter_vaccine_dose(self, request):
        """Get a list of vaccine_doses

        Args:
            - custom_user_code: String
            - injection_date_max: String vd:'2000-01-26T01:23:45.123456Z'
            - injection_date_min: String vd:'2000-01-26T01:23:45.123456Z'
            - page: int
            - page_size: int
            - search: String
        """

        accept_fields = [
            'custom_user_code',
            'injection_date_max', 'injection_date_min',
            'page', 'page_size', 'search',
        ]

        try:
            request_extractor = self.request_handler.handle(request)
            receive_fields = request_extractor.data
            accepted_fields = dict()

            for key in receive_fields.keys():
                if key in accept_fields:
                    accepted_fields[key] = receive_fields[key]

            validator = VaccineDoseValidator(**accepted_fields)

            validator.is_valid_fields([
                'injection_date_max', 'injection_date_min'
            ])
            validator.extra_validate_to_filter_vaccine_dose()

            query_set = VaccineDose.objects.all()

            list_to_filter_vaccine_dose = [key for key in accepted_fields.keys()]
            list_to_filter_vaccine_dose = set(list_to_filter_vaccine_dose) - \
            {'page', 'page_size'}

            dict_to_filter_vaccine_dose = validator.get_data(list_to_filter_vaccine_dose)

            dict_to_filter_vaccine_dose.setdefault('order_by', 'injection_date')

            filter = VaccineDoseFilter(dict_to_filter_vaccine_dose, queryset=query_set)

            query_set = filter.qs

            query_set = query_set.select_related()

            serializer = FilterVaccineDoseSerializer(query_set, many=True)

            paginated_data = paginate_data(request, serializer.data)

            return self.response_handler.handle(data=paginated_data)
        except Exception as exception:
            return self.exception_handler.handle(exception)
