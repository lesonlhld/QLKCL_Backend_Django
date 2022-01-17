from django.db import models
from address.models import Country, City, District, Ward
from user_account.models import CustomUser
from utils.enums import QuarantineWardStatus, QuarantineWardType

# Create your models here.

class QuarantineWard(models.Model):

    email = models.EmailField(
        verbose_name='email address',
        max_length=254,
        null=True,
        blank=True,
    )

    full_name = models.CharField(max_length=255, null=False)

    phone_number = models.CharField(max_length=16, null=True, blank=True)

    country = models.ForeignKey(
        to=Country,
        on_delete=models.SET_NULL,
        related_name='quarantine_ward_x_country',
        null=True,
        blank=True,
    )

    city = models.ForeignKey(
        to=City,
        on_delete=models.SET_NULL,
        related_name='quarantine_ward_x_city',
        null=True,
        blank=True,
    )

    district = models.ForeignKey(
        to=District,
        on_delete=models.SET_NULL,
        related_name='quarantine_ward_x_district',
        null=True,
        blank=True,
    )

    ward = models.ForeignKey(
        to=Ward,
        on_delete=models.SET_NULL,
        related_name='quarantine_ward_x_ward',
        null=True,
        blank=True,
    )

    address = models.TextField(null=True, blank=True)

    latitude = models.CharField(max_length=32, null=True, blank=True)

    longitude = models.CharField(max_length=32, null=True, blank=True)

    status = models.CharField(
        max_length=32,
        choices=QuarantineWardStatus.choices,
        default=QuarantineWardStatus.RUNNING,
        null=False,
    )

    type = models.CharField(
        max_length=32,
        choices=QuarantineWardType.choices,
        default=QuarantineWardType.CONCENTRATE,
        null=False,
    )

    quarantine_time = models.IntegerField(default=14, null=False)

    main_manager = models.ForeignKey(
        to=CustomUser,
        on_delete=models.SET_NULL,
        related_name='quarantine_ward_x_main_manager',
        null=True,
        blank=True,
    )

    trash = models.BooleanField(default=False, null=False)

    created_at = models.DateTimeField(auto_now_add=True, auto_now=False)

    created_by = models.ForeignKey(
        to=CustomUser,
        on_delete=models.SET_NULL,
        related_name='quarantine_ward_x_created_by',
        null=True,
        blank=True,
    )

    updated_at = models.DateTimeField(auto_now_add=False, auto_now=True)

    updated_by = models.ForeignKey(
        to=CustomUser,
        on_delete=models.SET_NULL,
        related_name='quarantine_ward_x_updated_by',
        null=True,
        blank=True,
    )

class QuarantineBuilding(models.Model):

    name = models.CharField(max_length=64, null=False)

    quarantine_ward = models.ForeignKey(
        to=QuarantineWard,
        on_delete=models.CASCADE,
        related_name='quarantine_building_x_quarantine_ward',
        null=False,
    )

class QuarantineFloor(models.Model):

    name = models.CharField(max_length=32, null=False)

    quarantine_building = models.ForeignKey(
        to=QuarantineBuilding,
        on_delete=models.CASCADE,
        related_name='quarantine_floor_x_quarantine_building',
        null=False,
    )

class QuarantineRoom(models.Model):

    name = models.CharField(max_length=16, null=False)

    capacity = models.IntegerField(default=4, null=False)

    quarantine_floor = models.ForeignKey(
        to=QuarantineFloor,
        on_delete=models.CASCADE,
        related_name='quarantine_room_x_quarantine_floor',
        null=False,
    )

    def __str__(self) -> str:
        return self.name
