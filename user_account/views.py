from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework import permissions
from rest_framework.decorators import action
from utils.views import AbstractView

# Create your views here.

class MemberAPI(AbstractView):

    permission_classes = [permissions.IsAuthenticated]

    @csrf_exempt
    @action(methods=['POST'], url_path='create', detail=False)
    def create_member(self, request):
        """Create a member

        Args:
            + 
        """

        # try:
        #     user = request.user
        #     if not user.role.name == 'ADMINISTRATOR':
        #         raise exceptions.AuthenticationException()

        #     disease_list = [
        #         'Tiểu đường', 'Ung thư', 'Hen suyễn', 'Tăng huyết áp',
        #         'Bệnh gan', 'Bệnh thận mãn tính', 'Bệnh tim mạch',
        #         'Bệnh lý mạch máu não', 'Bệnh khác',
        #     ]
            
        #     for name in disease_list:
        #         try:
        #             disease = BackgroundDisease.objects.get(name=name)
        #         except:
        #             disease = BackgroundDisease(name=name)
        #             disease.save()

        #     return self.response_handler.handle(data=messages.SUCCESS)
        # except Exception as exception:
        #     return self.exception_handler.handle(exception)