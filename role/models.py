from django.db import models
from utils.enums import RoleName

# Create your models here.

class Role(models.Model):

    name = models.CharField(
        max_length=32,
        choices=RoleName.choices,
        default=RoleName.MEMBER,
        unique=True,
        null=False,
    )

    created_at = models.DateTimeField(auto_now_add=True, auto_now=False)

    created_by = models.ForeignKey(
        to='user_account.CustomUser',
        on_delete=models.SET_NULL,
        related_name='role_x_created_by',
        null=True,
        blank=True,
    )

    updated_at = models.DateTimeField(auto_now_add=False, auto_now=True)

    updated_by = models.ForeignKey(
        to='user_account.CustomUser',
        on_delete=models.SET_NULL,
        related_name='role_x_updated_by',
        null=True,
        blank=True,
    )
