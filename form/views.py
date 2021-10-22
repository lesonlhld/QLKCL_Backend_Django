from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework import permissions
from rest_framework.decorators import action
from .models import BackgroundDisease, Symptom
from utils import exceptions, messages
from utils.enums import SymptomType
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
