import os
from random import randint
from django.db import models
from user_account.models import CustomUser
from utils.enums import SymptomType, TestStatus, TestResult, TestType, HealthDeclarationConclude

# Create your models here.

class BackgroundDisease(models.Model):

    name = models.CharField(max_length=64, unique=True, null=False)

    trash = models.BooleanField(default=False, null=False)

class Symptom(models.Model):

    name = models.CharField(max_length=64, unique=True, null=False)

    type = models.CharField(
        max_length=16,
        choices=SymptomType.choices,
        default=SymptomType.MAIN,
        null=False,
    )

    trash = models.BooleanField(default=False, null=False)

class MedicalDeclaration(models.Model):

    heartbeat = models.IntegerField(null=True, blank=True)

    temperature = models.FloatField(null=True, blank=True)

    breathing = models.IntegerField(null=True, blank=True)

    spo2 = models.FloatField(null=True, blank=True)

    blood_pressure = models.FloatField(null=True, blank=True)

    main_symptoms = models.TextField(null=True, blank=True)

    extra_symptoms = models.TextField(null=True, blank=True)

    other_symptoms = models.TextField(null=True, blank=True)

    conclude = models.CharField(
        max_length=32,
        choices=HealthDeclarationConclude.choices,
        default=HealthDeclarationConclude.NORMAL,
        null=False,
    )

    created_at = models.DateTimeField(auto_now_add=True, auto_now=False)

    created_by = models.ForeignKey(
        to=CustomUser,
        on_delete=models.SET_NULL,
        related_name='medical_declaration_x_created_by',
        null=True,
        blank=True,
    )

    user = models.ForeignKey(
        to=CustomUser,
        on_delete=models.SET_NULL,
        related_name='medical_declaration_x_user',
        null=True,
        blank=True,
    )

def test_code_generator():
    return ''.join(str(randint(0, 9)) for i in range(int(os.environ.get("TEST_CODE_LENGTH", '15'))))

class Test(models.Model):

    code = models.CharField(
        max_length=32,
        unique=True,
        default=test_code_generator,
        null=False,
    )

    status = models.CharField(
        max_length=16,
        choices=TestStatus.choices,
        default=TestStatus.WAITING,
        null=False,
    )

    result = models.CharField(
        max_length=16,
        choices=TestResult.choices,
        default=TestResult.NONE,
        null=False,
    )

    type = models.CharField(
        max_length=32,
        choices=TestType.choices,
        default=TestType.QUICK,
        null=False,
    )

    user = models.ForeignKey(
        to=CustomUser,
        on_delete=models.SET_NULL,
        related_name='test_user',
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True, auto_now=False)

    updated_at = models.DateTimeField(auto_now_add=False, auto_now=True)

    created_by = models.ForeignKey(
        to=CustomUser,
        on_delete=models.SET_NULL,
        related_name='test_x_created_by',
        null=True,
        blank=True,
    )

    updated_by = models.ForeignKey(
        to=CustomUser,
        on_delete=models.SET_NULL,
        related_name='test_x_updated_by',
        null=True,
        blank=True,
    )
