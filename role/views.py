from django.db import models
from django.shortcuts import render
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from rest_framework import permissions
from rest_framework.decorators import action
from .models import Role
from .serializers import RoleSerializer
from utils import exceptions, messages, validators
from utils.views import AbstractView

from datetime import datetime
import pytz
from form.models import Test
from form.serializers import TestSerializer

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
            if not user.role.name == 'ADMINISTRATOR':
                raise exceptions.AuthenticationException()
            
            try:
                validators.ModelInstanceExistenceValidator.valid(
                    model_cls=Role,
                    query_expr=Q(name='SUPER_MANAGER'),
                )
            except:
                super_manager_role = Role(name='SUPER_MANAGER', created_by=user)
                super_manager_role.save()
                
            try:
                validators.ModelInstanceExistenceValidator.valid(
                    model_cls=Role,
                    query_expr=Q(name='MANAGER'),
                )
            except:
                manager_role = Role(name='MANAGER', created_by=user)
                manager_role.save()

            try:
                validators.ModelInstanceExistenceValidator.valid(
                    model_cls=Role,
                    query_expr=Q(name='STAFF'),
                )
            except:
                staff_role = Role(name='STAFF', created_by=user)
                staff_role.save()

            try:
                validators.ModelInstanceExistenceValidator.valid(
                    model_cls=Role,
                    query_expr=Q(name='MEMBER'),
                )
            except:
                member_role = Role(name='MEMBER', created_by=user)
                member_role.save()

            return self.response_handler.handle(data=messages.SUCCESS)
        except Exception as exception:
            return self.exception_handler.handle(exception)

    @csrf_exempt
    @action(methods=['POST'], url_path='filter', detail=False)
    def filter_role(self, request):
        """Get a list of roles

        Args:
            None
        """

        try:
            serializer = RoleSerializer(Role.objects.all(), many=True)

            return self.response_handler.handle(data=serializer.data)
        except Exception as exception:
            return self.exception_handler.handle(exception)

class DebugAPI(AbstractView):

    @csrf_exempt
    @action(methods=['POST'], url_path='debug', detail=False)
    def debug(self, request):
        """For debug

        Args:
            
        """

        try:
            request_extractor = self.request_handler.handle(request)
            receive_fields = request_extractor.data
            vntz = pytz.timezone('Asia/Saigon')
            time_now = datetime.now(vntz)
            # print(time_now)
            new_time = time_now.astimezone(pytz.timezone('US/Eastern'))
            # print(new_time)

            time_1 = datetime.strptime('5/1/2005  1:33', '%m/%d/%Y %I:%M')
            time_1 = time_1.astimezone(vntz)
            print(time_1)



            return self.response_handler.handle(data="Success")
        except Exception as exception:
            return self.exception_handler.handle(exception)
