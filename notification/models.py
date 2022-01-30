from django.db import models
from user_account.models import CustomUser
from utils.enums import NotificationType

# Create your models here.

class Notification(models.Model):

    title = models.CharField(max_length=256, null=False)

    description = models.TextField(null=False)

    image = models.TextField(null=True, blank=True)

    url = models.CharField(max_length=2083, null=True, blank=True)

    type = models.CharField(
        max_length=32,
        choices=NotificationType.choices,
        default=NotificationType.PUSH,
        null=False,
    )

    created_at = models.DateTimeField(auto_now_add=True, auto_now=False)

    created_by = models.ForeignKey(
        to=CustomUser,
        on_delete=models.SET_NULL,
        related_name='notification_x_created_by',
        null=True,
        blank=True,
    )

class UserNotification(models.Model):

    class Meta:
        unique_together = [['user', 'notification', ], ]
        
    user = models.ForeignKey(
        to=CustomUser,
        on_delete=models.CASCADE,
        related_name='user_notification_x_user',
        null=False,
    )

    notification = models.ForeignKey(
        to=Notification,
        on_delete=models.CASCADE,
        related_name='user_notification_x_notification',
        null=False,
    )

    is_read = models.BooleanField(null=False, default=False)

    created_at = models.DateTimeField(auto_now_add=True, auto_now=False)

    created_by = models.ForeignKey(
        to=CustomUser,
        on_delete=models.SET_NULL,
        related_name='user_notification_x_created_by',
        null=True,
        blank=True,
    )
