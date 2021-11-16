from datetime import time
from django.db import models
from django.utils import timezone
from user_account.models import CustomUser
from utils.enums import ResetPasswordType

# Create your models here.
class ResetPasswordManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(
            created_at__gte=timezone.now()-timezone.timedelta(minutes=10)
        )

class ResetPassword(models.Model):

    objects = ResetPasswordManager()

    user = models.ForeignKey(
        to=CustomUser, 
        on_delete=models.CASCADE, 
        related_name='reset_password_x_user',
        null=False,
    )

    otp = models.CharField(max_length=10, null=False)

    type = models.CharField(
        max_length=32,
        choices=ResetPasswordType.choices,
        default=ResetPasswordType.USER_INPUT,
        null=False,
    )

    created_at = models.DateTimeField(auto_now=False, auto_now_add=True)

    created_by = models.ForeignKey(
        to=CustomUser,
        on_delete=models.SET_NULL,
        related_name='reset_password_x_created_by',
        null=True,
        blank=True,
    )

    def __str__(self):
        return f'{self.id}'