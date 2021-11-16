from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import action
from rest_framework import permissions
from utils import messages
from utils.views import AbstractView
from utils.tools import generateOTP
from utils.services import send_mail
from utils.enums import ResetPasswordType
from .models import ResetPassword
from user_account.models import CustomUser
from user_account.serializers import BaseCustomUserSerializer
from .validators.oauth import OauthValidator
from .serializers import ResetPasswordSerializer

# Create your views here.

class OauthAPI(AbstractView):
    
    permission_classes = [permissions.IsAuthenticated]

    @csrf_exempt
    @action(methods=['POST'], url_path='reset_password/set', detail=False)
    def reset_password(self, request):
        """Reset password: 
            - Check if email is valid or exist
            - Send to that email an OTP to activate reset action

        Args:
            + email (str)
        """

        accept_fields = [
            'email',
        ]

        require_fields = [
            'email',
        ]

        try:
            request_extractor = self.request_handler.handle(request)
            receive_fields = request_extractor.data
            accepted_fields = dict()

            for key in receive_fields:
                if key in accept_fields:
                    accepted_fields[key] = receive_fields[key]

            validator = OauthValidator(**accepted_fields)
            validator.is_missing_fields(require_fields)
            validator.is_valid_fields(accepted_fields)

            user_email = validator.get_field('email')
            user = CustomUser.objects.get(email=user_email)

            reset_password_for_user = ResetPassword.objects.create(
                user=user,
                otp=generateOTP(4),
            )

            subject = 'Mã đặt lại mật khẩu'
            message = 'Nhập mã OTP: ' + reset_password_for_user.otp

            send_mail(
                subject=subject,
                message=message,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[user.email],
            )

            serializer = BaseCustomUserSerializer(user, many=False)
            return self.response_handler.handle(data=serializer.data)
        except Exception as exception:
            return self.exception_handler.handle(exception)

    @csrf_exempt
    @action(methods=['POST'], url_path='reset_password/otp', detail=False)
    def confirm_otp(self, request):
        """Confirm otp: Check if otp is valid
            - Remove current otp and create new otp for system handling if valid 

        Args:
            + otp (str)
        """

        accept_fields = [
            'otp',
        ]

        required_fields = [
            'otp',
        ]

        try:
            request_extractor = self.request_handler.handle(request)
            receive_fields = request_extractor.data
            accepted_fields = dict()

            for key in receive_fields:
                if key in accept_fields:
                    accepted_fields[key] = receive_fields[key]

            print(request.user)
            accepted_fields['user'] = request.user

            validator = OauthValidator(**accepted_fields)
            validator.is_missing_fields(required_fields)
            validator.is_valid_fields(accepted_fields)

            old_reset_password = ResetPassword.objects.get(user=request.user)
            old_reset_password.delete()

            new_reset_password = ResetPassword.objects.create(
                user=request.user,
                otp=generateOTP(4),
                type=ResetPasswordType.SYSTEM_HANDLE,
            )
            serializer = ResetPasswordSerializer(new_reset_password, many=False)
            
            return self.response_handler.handle(data=serializer.data)
        except Exception as exception:
            return self.exception_handler.handle(exception)
    
    @csrf_exempt
    @action(methods=['POST'], url_path='reset_password/confirm', detail=False)
    def confirm_reset_password(self, request):
        """Confirm Reset Password: 
            - Change Password
            - Check if confirmed otp (otp for system) is valid then remove that otp and update password 
        Args:
            + new_password (str)
            + confirm_password (str)
        """

        accept_fields = [
            'new_password', 'confirm_password', 'confirm_otp'
        ]

        required_fields = [
            'new_password', 'confirm_password', 'confirm_otp'
        ]

        try:
            request_extractor = self.request_handler.handle(request)
            receive_fields = request_extractor.data
            accepted_fields = dict()

            for key in receive_fields:
                if key in accept_fields:
                    accepted_fields[key] = receive_fields[key]

            accepted_fields['user'] = request.user

            validator = OauthValidator(**accepted_fields)
            validator.is_missing_fields(required_fields)
            validator.is_valid_fields(accepted_fields)

            new_password = validator.get_field('confirm_password')

            user = request.user
            user.set_password(new_password)
            user.save()

            reset_password = ResetPassword.objects.get(user=user)
            reset_password.delete()
            
            return self.response_handler.handle(data=messages.SUCCESS)
        except Exception as exception:
            return self.exception_handler.handle(exception)
        
    @csrf_exempt
    @action(methods=['POST'], url_path='change_password', detail=False)
    def change_password(self, request):
        """Change password: 
            - Check if new password is the same with old password and confirm password is match with new password 
        Args:
            + old_password (str)
            + new_password (str)
            + confirm_password (str)
        """

        accept_fields = [
            'old_password', 'new_password', 'confirm_password',
        ]

        required_fields = [
            'old_password', 'new_password', 'confirm_password', 
        ]

        try:
            request_extractor = self.request_handler.handle(request)
            receive_fields = request_extractor.data
            accepted_fields = dict()

            for key in receive_fields:
                if key in accept_fields:
                    accepted_fields[key] = receive_fields[key]

            accepted_fields['user'] = request.user

            validator = OauthValidator(**accepted_fields)
            validator.is_missing_fields(required_fields)
            validator.is_valid_fields(accepted_fields)

            new_password = validator.get_field('confirm_password')

            user = request.user
            user.set_password(new_password)
            user.save()
            
            return self.response_handler.handle(data=messages.SUCCESS)
        except Exception as exception:
            return self.exception_handler.handle(exception)

