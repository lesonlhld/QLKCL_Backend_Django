from django.db import models
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework import permissions
from rest_framework.decorators import action
from .models import Role
from utils import exceptions, messages
from utils.views import AbstractView

# Create your views here.

class RoleAPI(AbstractView):

    permission_classes = [permissions.IsAuthenticated]

    @csrf_exempt
    @action(methods=['POST'], url_path='init', detail=False)
    def init_role(self, request):
        """Init some base role

        Args:
            None
        """

        try:
            user = request.user
            if not user.admin:
                raise exceptions.AuthenticationException()

            try:
                administrator_role = Role.objects.get(name='ADMINISTRATOR')
            except:
                administrator_role = Role(name='ADMINISTRATOR', created_by=user)
                administrator_role.save()
            
            try:
                super_manager_role = Role.objects.get(name='SUPER_MANAGER')
            except:
                super_manager_role = Role(name='SUPER_MANAGER', created_by=user)
                super_manager_role.save()
                
            try:
                manager_role = Role.objects.get(name='MANAGER')
            except:
                manager_role = Role(name='MANAGER', created_by=user)
                manager_role.save()

            try:
                staff_role = Role.objects.get(name='STAFF')
            except:
                staff_role = Role(name='STAFF', created_by=user)
                staff_role.save()

            try:
                member_role = Role.objects.get(name='MEMBER')
            except:
                member_role = Role(name='MEMBER', created_by=user)
                member_role.save()

            return self.response_handler.handle(data=messages.SUCCESS)
        except Exception as exception:
            return self.exception_handler.handle(exception)
