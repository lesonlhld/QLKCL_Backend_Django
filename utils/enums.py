from enum import unique
from django.db import models

@unique
class QuarantineWardStatus(models.TextChoices):
    LOCKED = 'LOCKED'
    RUNNING = 'RUNNING'
    UNKNOWN = 'UNKNOWN'

class CustomUserStatus(models.TextChoices):
    WAITING = 'WAITING'
    REFUSED = 'REFUSED'
    LOCKED = 'LOCKED'
    AVAILABLE = 'AVAILABLE'
    LEAVE = 'LEAVE'

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

class MemberLabel(models.TextChoices):
    F0 = 'F0'
    F1 = 'F1'
    F2 = 'F2'
    F3 = 'F3'
    FROM_EPIDEMIC_AREA = 'FROM_EPIDEMIC_AREA'
    ABROAD = 'ABROAD'

class MemberQuarantinedStatus(models.TextChoices):
    COMPLETED = 'COMPLETED'
    QUARANTINING = 'QUARANTINING'
    HOSPITALIZE = 'HOSPITALIZE'
    MOVED = 'MOVED'

class QuarantineHistoryStatus(models.TextChoices):
    PRESENT = 'PRESENT'
    ENDED = 'ENDED'

class QuarantineHistoryEndType(models.TextChoices):
    HOSPITALIZE = 'HOSPITALIZE'
    COMPLETED = 'COMPLETED'
    CHANGE_ROOM = 'CHANGE_ROOM'

class HealthStatus(models.TextChoices):
    NORMAL = 'NORMAL'
    UNWELL = 'UNWELL'
    SERIOUS = 'SERIOUS'

class HealthDeclarationConclude(models.TextChoices):
    NORMAL = 'NORMAL'
    UNWELL = 'UNWELL'
    SERIOUS = 'SERIOUS'

class Disease(models.TextChoices):
    # now not use
    NONE = 'NONE'
    TIEU_DUONG = 'TIEU_DUONG'
    UNG_THU = 'UNG_THU'
    HEN_SUYEN = 'HEN_SUYEN'
    CAO_HUYET_AP = 'CAO_HUYET_AP'
    BENH_GAN = 'BENH_GAN'
    BENH_THAN_MAN_TINH = 'BENH_THAN_MAN_TINH'
    BENH_TIM_MACH = 'BENH_TIM_MACH'
    BENH_LY_MACH_MAU_NAO = 'BENH_LY_MACH_MAU_NAO'
    OTHER = 'OTHER'

class SymptomType(models.TextChoices):
    MAIN = 'MAIN'
    EXTRA = 'EXTRA'

class TestStatus(models.TextChoices):
    WAITING = 'WAITING'
    DONE = 'DONE'

class TestResult(models.TextChoices):
    NONE = 'NONE'
    NEGATIVE = 'NEGATIVE'
    POSITIVE = 'POSITIVE'

class TestType(models.TextChoices):
    QUICK = 'QUICK'
    RT_PCR = 'RT-PCR'

class ResetPasswordType(models.TextChoices):
    USER_INPUT = 'USER_INPUT'
    SYSTEM_HANDLE = 'SYSTEM_HANDLE'

class NotificationType(models.TextChoices):
    PUSH = 'PUSH'
    EMAIL = 'EMAIL'
    SMS = 'SMS'

class Professional(models.TextChoices):
    VIEN_CHUC = 'Viên chức / Nhân viên'
    CONG_CHUC = 'Công chức'
    CONG_NHAN = 'Công nhân'
    KINH_DOANH = 'Buôn bán / Kinh doanh'
    DOANH_NGHIEP = 'Doanh nghiệp / Sale'
    LAO_DONG = 'Lao động tự do'
    HUU_TRI = 'Hưu trí'
    KE_TOAN = 'Kế toán'
    NHAN_VIEN_VAN_PHONG = 'Nhân viên văn phòng'
    CONG_AN = 'Công an'
    LAM_NONG = 'Làm nông'
    SINH_VIEN = 'Sinh viên'
    PHONG_VIEN = 'Phóng viên'
    LAI_XE = 'Lái xe'
    LUAT_SU = 'Luật sư'
    KY_SU = 'Kỹ sư'
    NHAN_VIEN_Y_TE = 'Nhân viên y tế'
    NGHE_SI = 'Nghệ sĩ / KOLs'