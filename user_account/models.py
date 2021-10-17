from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.db import models
from address.models import Country, City, District, Ward
from role.models import Role
from utils.enums import Gender, CustomUserStatus, RoleName

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
        user = CustomUser(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_administrator(self, phone_number, password, **extra_fields):
        """
        Create and save a Administrator with the given phone number and password.
        """
        admin_role = Role.objects.get(name=RoleName.ADMINISTRATOR)
        extra_fields.setdefault('role', admin_role)

        if extra_fields.get('role') is not admin_role:
            raise ValueError('Superuser must have role=ADMINISTRATOR')
        return self.create_user(phone_number, password, **extra_fields)

    def delete_user(self, phone_number):
        user = CustomUser.objects.get(phone_number=phone_number)
        user.delete()

class CustomUser(AbstractBaseUser):

    objects = CustomUserManager()

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = [] # Phone number & Password are required by default.

    email = models.EmailField(
        verbose_name='email address',
        max_length=254,
        null=True,
        blank=True,
    )

    first_name = models.CharField(max_length=128, null=True, blank=True)

    last_name = models.CharField(max_length=128, null=True, blank=True)

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

    address = models.TextField(null=True, blank=True)

    health_insurance_number = models.CharField(max_length=64, null=True, blank=True)

    identity_number = models.CharField(max_length=12, null=True, blank=True)

    verified = models.BooleanField(default=False, null=False)

    status = models.CharField(
        max_length=32,
        choices=CustomUserStatus.choices,
        default=CustomUserStatus.AVAILABLE,
        null=False,
    )

    quanrantine_ward = models.ForeignKey(
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
