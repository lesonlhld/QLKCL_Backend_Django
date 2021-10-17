from enum import unique
from django.db import models

@unique
class QuarantineWardStatus(models.TextChoices):
    LOCKED = 'LOCKED',
    RUNNING = 'RUNNING'
    UNKNOWN = 'UNKNOWN'

class CustomUserStatus(models.TextChoices):
    LOCKED = 'LOCKED',
    AVAILABLE = 'AVAILABLE'

class QuarantineWardType(models.TextChoices):
    CONCENTRATE = 'CONCENTRATE'
    PRIVATE = 'PRIVATE'

class Gender(models.TextChoices):
    MALE = 'MALE'
    FEMALE = 'FEMALE'

class RoleName(models.TextChoices):
    ADMINISTRATOR = 'ADMINISTRATOR'
    SUPER_MANAGER = 'SUPER_MANAGER'
    MANAGER = 'MANAGER'
    STAFF = 'STAFF'
    MEMBER = 'MEMBER'
