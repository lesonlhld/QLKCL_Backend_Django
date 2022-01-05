import os
from random import randint
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.db import models
from django.db.models import Q
from address.models import Country, City, District, Ward
from role.models import Role
from utils.enums import (
    Gender,
    CustomUserStatus,
    RoleName,
    MemberLabel,
    MemberQuarantinedStatus,
    HealthStatus,
    Disease,
)
from utils import validators

def user_code_generator():
    return ''.join(str(randint(0, 9)) for i in range(int(os.environ.get("USER_CODE_LENGTH", '15'))))

# Create your models here.

class CustomUserManager(BaseUserManager):
    """
    Custom user model manager where phone_number is the unique identifiers
    for authentication instead of usernames.
    """
    def create_user(self, phone_number, password, **extra_fields):
        """
        Create and save a User with the given phone number and password.
        """
        if not phone_number:
            raise ValueError('Users must have an phone number')
        custom_user = CustomUser(phone_number=phone_number, **extra_fields)
        custom_user.set_password(password)
        custom_user.save()

        return custom_user

    def create_administrator(self, phone_number, password, **extra_fields):
        """
        Create and save a Administrator with the given phone number and password.
        """
        role = None
        try:
            role = validators.ModelInstanceExistenceValidator.valid(
                model_cls=Role,
                query_expr=Q(name='ADMINISTRATOR'),
            )
        except Exception as exception:
            role = Role(name='ADMINISTRATOR')
            role.save()
        
        extra_fields.setdefault('role', role)

        return self.create_user(phone_number, password, **extra_fields)

    def delete_user(self, phone_number):
        user = CustomUser.objects.get(phone_number=phone_number)
        user.delete()

class CustomUser(AbstractBaseUser):

    objects = CustomUserManager()

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = [] # Phone number & Password are required by default.

    code = models.CharField(
        max_length=18,
        unique=True,
        default=user_code_generator,
        null=False,
    )

    email = models.EmailField(
        verbose_name='email address',
        max_length=254,
        unique=True,
        null=True,
        blank=True,
    )

    full_name = models.CharField(max_length=256, null=False)

    phone_number = models.CharField(max_length=16, unique=True, null=False)

    birthday = models.CharField(max_length=10, null=True, blank=True)

    gender = models.CharField(
        max_length=12,
        choices=Gender.choices,
        default=Gender.MALE,
        null=False,
    )

    nationality = models.ForeignKey(
        to=Country,
        on_delete=models.SET_NULL,
        related_name='custom_user_x_nationality',
        null=True,
        blank=True,
    )

    country = models.ForeignKey(
        to=Country,
        on_delete=models.SET_NULL,
        related_name='custom_user_x_country',
        null=True,
        blank=True,
    )

    city = models.ForeignKey(
        to=City,
        on_delete=models.SET_NULL,
        related_name='custom_user_x_city',
        null=True,
        blank=True,
    )

    district = models.ForeignKey(
        to=District,
        on_delete=models.SET_NULL,
        related_name='custom_user_x_district',
        null=True,
        blank=True,
    )

    ward = models.ForeignKey(
        to=Ward,
        on_delete=models.SET_NULL,
        related_name='custom_user_x_ward',
        null=True,
        blank=True,
    )

    detail_address = models.TextField(null=True, blank=True)

    health_insurance_number = models.CharField(max_length=64, unique=True, null=True, blank=True)

    identity_number = models.CharField(max_length=12, unique=True, null=True, blank=True)

    passport_number = models.CharField(max_length=12, unique=True, null=True, blank=True)

    email_verified = models.BooleanField(default=False, null=False)

    status = models.CharField(
        max_length=32,
        choices=CustomUserStatus.choices,
        default=CustomUserStatus.AVAILABLE,
        null=False,
    )

    quarantine_ward = models.ForeignKey(
        to='quarantine_ward.QuarantineWard',
        on_delete=models.SET_NULL,
        related_name='custom_user_x_quanrantine_ward',
        null=True,
        blank=True,
    )

    role = models.ForeignKey(
        to='role.Role',
        on_delete=models.SET_NULL,
        related_name='custom_user_x_role',
        null=True,
        blank=True,
    )

    trash = models.BooleanField(default=False, null=False)

    created_at = models.DateTimeField(auto_now_add=True, auto_now=False)

    created_by = models.ForeignKey(
        to='user_account.CustomUser',
        on_delete=models.SET_NULL,
        related_name='custom_user_x_created_by',
        null=True,
        blank=True,
    )

    updated_at = models.DateTimeField(auto_now_add=False, auto_now=True)

    updated_by = models.ForeignKey(
        to='user_account.CustomUser',
        on_delete=models.SET_NULL,
        related_name='custom_user_x_updated_by',
        null=True,
        blank=True,
    )

class Member(models.Model):

    custom_user = models.OneToOneField(
        to=CustomUser,
        on_delete=models.CASCADE,
        related_name='member_x_custom_user',
        primary_key=False,
        null=False,
    )

    label = models.CharField(
        max_length=8,
        choices=MemberLabel.choices,
        default=MemberLabel.F0,
        null=False,
    )

    positive_tested_before = models.BooleanField(default=False, null=False)

    abroad = models.BooleanField(default=False, null=False)

    quarantined_at = models.DateTimeField(auto_now_add=False, auto_now=False, null=True, blank=True)

    quarantined_finished_at = models.DateTimeField(auto_now_add=False, auto_now=False, null=True, blank=True)

    quarantined_status = models.CharField(
        max_length=32,
        choices=MemberQuarantinedStatus.choices,
        default=MemberQuarantinedStatus.QUARANTINING,
        null=False,
    )

    last_tested = models.DateTimeField(auto_now_add=False, auto_now=False, null=True, blank=True)

    last_tested_had_result = models.DateTimeField(auto_now_add=False, auto_now=False, null=True, blank=True)

    health_status = models.CharField(
        max_length=32,
        choices=HealthStatus.choices,
        default=HealthStatus.NORMAL,
        null=False,
    )

    health_note = models.TextField(null=True, blank=True)

    positive_test = models.BooleanField(null=True, blank=True)

    care_staff = models.ForeignKey(
        to=CustomUser,
        on_delete=models.SET_NULL,
        related_name='member_x_care_staff',
        null=True,
        blank=True,
    )

    background_disease = models.TextField(null=True, blank=True)

    other_background_disease = models.TextField(null=True, blank=True)

    background_disease_note = models.TextField(null=True, blank=True)

    quarantine_room = models.ForeignKey(
        to='quarantine_ward.QuarantineRoom',
        on_delete=models.SET_NULL,
        related_name='member_x_quarantine_room',
        null=True,
        blank=True,
    )

    @property
    def quarantine_floor(self):
        if self.quarantine_room:
            return self.quarantine_room.quarantine_floor
        else:
            return None

    @property
    def quarantine_building(self):
        if self.quarantine_floor:
            return self.quarantine_floor.quarantine_building
        else:
            return None

    @property
    def quarantine_ward(self):
        if self.quarantine_building:
            return self.quarantine_building.quarantine_ward
        else:
            return None

class Manager(models.Model):

    custom_user = models.OneToOneField(
        to=CustomUser,
        on_delete=models.CASCADE,
        related_name='manager_x_custom_user',
        primary_key=False,
        null=False,
    )

    last_tested = models.DateTimeField(auto_now_add=False, auto_now=False, null=True, blank=True)

    last_tested_had_result = models.DateTimeField(auto_now_add=False, auto_now=False, null=True, blank=True)

    health_status = models.CharField(
        max_length=32,
        choices=HealthStatus.choices,
        default=HealthStatus.NORMAL,
        null=False,
    )

    health_note = models.TextField(null=True, blank=True)

    positive_test_now = models.BooleanField(null=True, blank=True)

class Staff(models.Model):

    custom_user = models.OneToOneField(
        to=CustomUser,
        on_delete=models.CASCADE,
        related_name='staff_x_custom_user',
        primary_key=False,
        null=False,
    )

    last_tested = models.DateTimeField(auto_now_add=False, auto_now=False, null=True, blank=True)

    last_tested_had_result = models.DateTimeField(auto_now_add=False, auto_now=False, null=True, blank=True)

    health_status = models.CharField(
        max_length=32,
        choices=HealthStatus.choices,
        default=HealthStatus.NORMAL,
        null=False,
    )

    health_note = models.TextField(null=True, blank=True)

    positive_test_now = models.BooleanField(null=True, blank=True)

    care_area = models.TextField(null=True, blank=True)
