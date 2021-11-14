import os
import datetime
from django.db.models import Q
from ..models import CustomUser, Member
from address.models import Country, City, District, Ward
from quarantine_ward.models import QuarantineWard, QuarantineRoom
from form.models import BackgroundDisease
from utils import validators, messages, exceptions
from utils.enums import Gender, MemberLabel, CustomUserStatus, HealthStatus
from utils.tools import split_input_list, date_string_to_timestamp, timestamp_string_to_date_string

class UserValidator(validators.AbstractRequestValidate):

    def is_valid_fields(self, keys: list):
        ignorable_fields = {}
        set_of_keys = set(keys)

        return super().is_valid_fields(set_of_keys)

    def is_validate_phone_number(self):
        if hasattr(self, '_phone_number'):
            self._phone_number = validators.PhoneNumberValidator.valid(self._phone_number)

    def is_validate_password(self):
        if hasattr(self, '_password'):
            value = self._password
            validators.PasswordValidator.valid(value)

    def is_validate_email(self):
        if hasattr(self, '_email'):
            self._email = validators.EmailValidator.valid(self._email)

    def is_validate_birthday(self):
        if hasattr(self, '_birthday'):
            self._birthday = validators.DateStringValidator.valid(
                self._birthday,
                message={'birthday': messages.INVALID}
            )

    def is_validate_gender(self):
        if hasattr(self, '_gender'):
            self._gender = validators.EnumValidator.valid(
                value=self._gender,
                enum_cls=Gender,
                message={'gender': messages.INVALID},
            )

    def is_validate_label(self):
        if hasattr(self, '_label'):
            self._label = validators.EnumValidator.valid(
                value=self._label,
                enum_cls=MemberLabel,
                message={'label': messages.INVALID},
            )

    def is_validate_status(self):
        if hasattr(self, '_status'):
            self._status = validators.EnumValidator.valid(
                value=self._status,
                enum_cls=CustomUserStatus,
                message={'status': messages.INVALID},
            )

    def is_validate_positive_test(self):
        if hasattr(self, '_positive_test'):
            self._positive_test = validators.BooleanValidator.valid(
                value=self._positive_test,
                message={'positive_test': messages.INVALID},
            )

    def is_validate_health_status_list(self):
        if hasattr(self, '_health_status_list'):
            self._new_health_status_list = split_input_list(self._health_status_list)
            for item in self._new_health_status_list:
                item = validators.EnumValidator.valid(
                    value=item,
                    enum_cls=HealthStatus,
                    message={'health_status': messages.INVALID},
                )

    def is_validate_is_last_tested(self):
        if hasattr(self, '_is_last_tested'):
            self._is_last_tested = validators.BooleanValidator.valid(
                value=self._is_last_tested,
                message={'is_last_tested': messages.INVALID},
            )

    def is_validate_quarantined_at(self):
        if hasattr(self, '_quarantined_at'):
            self._quarantined_at = validators.DateStringValidator.valid(
                self._quarantined_at,
                message={'quarantined_at': messages.INVALID}
            )

    def is_validate_positive_tested_before(self):
        if hasattr(self, '_positive_tested_before'):
            self._positive_tested_before = validators.BooleanValidator.valid(
                self._positive_tested_before,
                message={'positive_tested_before': messages.INVALID},
            )

    def is_validate_can_finish_quarantine(self):
        if hasattr(self, '_can_finish_quarantine'):
            self._can_finish_quarantine = validators.BooleanValidator.valid(
                self._can_finish_quarantine,
                message={'can_finish_quarantine': messages.INVALID},
            )
        
    def is_validate_background_disease(self):
        if hasattr(self, '_background_disease'):
            self._list_background_disease_objects = []
            self._list_background_disease_ids = split_input_list(self._background_disease)
            for item in self._list_background_disease_ids:
                try:
                    object = validators.ModelInstanceExistenceValidator.valid(
                        model_cls=BackgroundDisease,
                        query_expr=Q(id=item),
                    )
                    self._list_background_disease_objects += [object]
                except Exception as exception:
                    raise exceptions.NotFoundException({'background_disease': messages.NOT_EXIST})

    def is_id_exist(self):
        if hasattr(self, '_id'):
            try:
                self._custom_user = validators.ModelInstanceExistenceValidator.valid(
                    model_cls=CustomUser,
                    query_expr=Q(id=self._id),
                )
                return True
            except Exception as exception:
                return False
        return False

    def is_email_exist(self):
        if hasattr(self, '_email'):
            try:
                validators.ModelInstanceExistenceValidator.valid(
                    model_cls=CustomUser,
                    query_expr=Q(email=self._email),
                )
                return True
            except Exception as exception:
                return False
        return False

    def is_new_email_valid(self):
        if hasattr(self, '_email'):
            try:
                found_user = validators.ModelInstanceExistenceValidator.valid(
                    model_cls=CustomUser,
                    query_expr=Q(email=self._email),
                )
                if found_user == self._custom_user:
                    return True
                else:
                    return False
            except Exception as exception:
                return True
        return False

    def is_health_insurance_number_exist(self):
        if hasattr(self, '_health_insurance_number'):
            try:
                validators.ModelInstanceExistenceValidator.valid(
                    model_cls=CustomUser,
                    query_expr=Q(health_insurance_number=self._health_insurance_number),
                )
                return True
            except Exception as exception:
                return False
        return False

    def is_new_health_insurance_number_valid(self):
        if hasattr(self, '_health_insurance_number'):
            try:
                found_user = validators.ModelInstanceExistenceValidator.valid(
                    model_cls=CustomUser,
                    query_expr=Q(health_insurance_number=self._health_insurance_number),
                )
                if found_user == self._custom_user:
                    return True
                else:
                    return False
            except Exception as exception:
                return True
        return False

    def is_identity_number_exist(self):
        if hasattr(self, '_identity_number'):
            try:
                validators.ModelInstanceExistenceValidator.valid(
                    model_cls=CustomUser,
                    query_expr=Q(identity_number=self._identity_number),
                )
                return True
            except Exception as exception:
                return False
        return False

    def is_new_identity_number_valid(self):
        if hasattr(self, '_identity_number'):
            try:
                found_user = validators.ModelInstanceExistenceValidator.valid(
                    model_cls=CustomUser,
                    query_expr=Q(identity_number=self._identity_number),
                )
                if found_user == self._custom_user:
                    return True
                else:
                    return False
            except Exception as exception:
                return True
        return False

    def is_passport_number_exist(self):
        if hasattr(self, '_passport_number'):
            try:
                validators.ModelInstanceExistenceValidator.valid(
                    model_cls=CustomUser,
                    query_expr=Q(passport_number=self._passport_number),
                )
                return True
            except Exception as exception:
                return False
        return False

    def is_new_passport_number_valid(self):
        if hasattr(self, '_passport_number'):
            try:
                found_user = validators.ModelInstanceExistenceValidator.valid(
                    model_cls=CustomUser,
                    query_expr=Q(passport_number=self._passport_number),
                )
                if found_user == self._custom_user:
                    return True
                else:
                    return False
            except Exception as exception:
                return True
        return False

    def get_user_by_code(self, code):
        try:
            user = validators.ModelInstanceExistenceValidator.valid(
                model_cls=CustomUser,
                query_expr=Q(code=code),
            )
            return user
        except Exception as exception:
            return None
        
    def is_code_exist(self, code=None):
        if code:
            try:
                value = code
                validators.ModelInstanceExistenceValidator.valid(
                    model_cls=CustomUser,
                    query_expr=Q(code=value),
                )
                return True
            except Exception as exception:
                return False
        else:
            if hasattr(self, '_code'):
                try:
                    self._custom_user = validators.ModelInstanceExistenceValidator.valid(
                        model_cls=CustomUser,
                        query_expr=Q(code=self._code),
                    )
                    return True
                except Exception as exception:
                    return False
            return True

    def is_phone_number_exist(self):
        if hasattr(self, '_phone_number'):
            try:
                self._custom_user = validators.ModelInstanceExistenceValidator.valid(
                    model_cls=CustomUser,
                    query_expr=Q(phone_number=self._phone_number),
                )
                return True
            except Exception as exception:
                return False
        return False

    def is_nationality_code_exist(self):
        if hasattr(self, '_nationality_code'):
            try:
                self._nationality = validators.ModelInstanceExistenceValidator.valid(
                    model_cls=Country,
                    query_expr=Q(code=self._nationality_code),
                )
                return True
            except Exception as exception:
                return False
        return False

    def is_country_code_exist(self):
        if hasattr(self, '_country_code'):
            try:
                self._country = validators.ModelInstanceExistenceValidator.valid(
                    model_cls=Country,
                    query_expr=Q(code=self._country_code),
                )
                return True
            except Exception as exception:
                return False
        return False

    def is_city_id_exist(self):
        if hasattr(self, '_city_id'):
            try:
                self._city = validators.ModelInstanceExistenceValidator.valid(
                    model_cls=City,
                    query_expr=Q(id=self._city_id),
                )
                return True
            except Exception as exception:
                return False
        return False

    def is_district_id_exist(self):
        if hasattr(self, '_district_id'):
            try:
                self._district = validators.ModelInstanceExistenceValidator.valid(
                    model_cls=District,
                    query_expr=Q(id=self._district_id),
                )
                return True
            except Exception as exception:
                return False
        return False

    def is_ward_id_exist(self):
        if hasattr(self, '_ward_id'):
            try:
                self._ward = validators.ModelInstanceExistenceValidator.valid(
                    model_cls=Ward,
                    query_expr=Q(id=self._ward_id),
                )
                return True
            except Exception as exception:
                return False
        return False

    def is_quarantine_ward_id_exist(self):
        if hasattr(self, '_quarantine_ward_id'):
            try:
                self._quarantine_ward = validators.ModelInstanceExistenceValidator.valid(
                    model_cls=QuarantineWard,
                    query_expr=Q(id=self._quarantine_ward_id),
                )
                return True
            except Exception as exception:
                return False
        return True

    def is_quarantine_room_id_exist(self):
        if hasattr(self, '_quarantine_room_id'):
            try:
                self._quarantine_room = validators.ModelInstanceExistenceValidator.valid(
                    model_cls=QuarantineRoom,
                    query_expr=Q(id=self._quarantine_room_id),
                )
                return True
            except Exception as exception:
                return False
        return True

    def extra_validate_to_register_member(self):
        if hasattr(self, '_phone_number') and self.is_phone_number_exist():
            raise exceptions.ValidationException({'phone_number': messages.EXIST})
        if hasattr(self, '_quarantine_ward_id') and not self.is_quarantine_ward_id_exist():
            raise exceptions.NotFoundException({'quarantine_ward_id': messages.NOT_EXIST})

    def extra_validate_to_create_member(self):
        if hasattr(self, '_phone_number') and self.is_phone_number_exist():
            raise exceptions.ValidationException({'phone_number': messages.EXIST})
        if hasattr(self, '_email') and self.is_email_exist():
            raise exceptions.ValidationException({'email': messages.EXIST})
        if hasattr(self, '_health_insurance_number') and self.is_health_insurance_number_exist():
            raise exceptions.ValidationException({'health_insurance_number': messages.EXIST})
        if hasattr(self, '_identity_number') and self.is_identity_number_exist():
            raise exceptions.ValidationException({'identity_number': messages.EXIST})
        if hasattr(self, '_passport_number') and self.is_passport_number_exist():
            raise exceptions.ValidationException({'passport_number': messages.EXIST})
        if hasattr(self, '_nationality_code') and not self.is_nationality_code_exist():
            raise exceptions.NotFoundException({'nationality_code': messages.NOT_EXIST})
        if hasattr(self, '_country_code') and not self.is_country_code_exist():
            raise exceptions.NotFoundException({'country_code': messages.NOT_EXIST})
        if hasattr(self, '_city_id') and not self.is_city_id_exist():
            raise exceptions.NotFoundException({'city_id': messages.NOT_EXIST})
        if hasattr(self, '_district_id') and not self.is_district_id_exist():
            raise exceptions.NotFoundException({'district_id': messages.NOT_EXIST})
        if hasattr(self, '_ward_id') and not self.is_ward_id_exist():
            raise exceptions.NotFoundException({'ward_id': messages.NOT_EXIST})
        if hasattr(self, '_quarantine_ward_id') and not self.is_quarantine_ward_id_exist():
            raise exceptions.NotFoundException({'quarantine_ward_id': messages.NOT_EXIST})
        if hasattr(self, '_quarantine_room_id') and not self.is_quarantine_room_id_exist():
            raise exceptions.NotFoundException({'quarantine_room_id': messages.NOT_EXIST})

    def extra_validate_to_update_user(self):
        if hasattr(self, '_code') and not self.is_code_exist():
            raise exceptions.NotFoundException({'code': messages.NOT_EXIST})
        if hasattr(self, '_email') and not self.is_new_email_valid():
            raise exceptions.NotFoundException({'email': messages.EXIST})
        if hasattr(self, '_health_insurance_number') and not self.is_new_health_insurance_number_valid():
            raise exceptions.NotFoundException({'health_insurance_number': messages.EXIST})
        if hasattr(self, '_identity_number') and not self.is_new_identity_number_valid():
            raise exceptions.NotFoundException({'identity_number': messages.EXIST})
        if hasattr(self, '_passport_number') and not self.is_new_passport_number_valid():
            raise exceptions.NotFoundException({'passport_number': messages.EXIST})
        if hasattr(self, '_nationality_code') and not self.is_nationality_code_exist():
            raise exceptions.NotFoundException({'nationality_code': messages.NOT_EXIST})
        if hasattr(self, '_country_code') and not self.is_country_code_exist():
            raise exceptions.NotFoundException({'country_code': messages.NOT_EXIST})
        if hasattr(self, '_city_id') and not self.is_city_id_exist():
            raise exceptions.NotFoundException({'city_id': messages.NOT_EXIST})
        if hasattr(self, '_district_id') and not self.is_district_id_exist():
            raise exceptions.NotFoundException({'district_id': messages.NOT_EXIST})
        if hasattr(self, '_ward_id') and not self.is_ward_id_exist():
            raise exceptions.NotFoundException({'ward_id': messages.NOT_EXIST})
        if hasattr(self, '_quarantine_ward_id') and not self.is_quarantine_ward_id_exist():
            raise exceptions.NotFoundException({'quarantine_ward_id': messages.NOT_EXIST})
        if hasattr(self, '_quarantine_room_id') and not self.is_quarantine_room_id_exist():
            raise exceptions.NotFoundException({'quarantine_room_id': messages.NOT_EXIST})

    def extra_validate_to_accept_member(self):
        if hasattr(self, '_member_codes'):
            self._member_codes = split_input_list(self._member_codes)
            self._members = []
            for code in self._member_codes:
                user = self.get_user_by_code(code)
                if not user:
                    raise exceptions.NotFoundException({'main': messages.MEMBER_NOT_FOUND})
                if hasattr(user, 'member_x_custom_user') and not user.member_x_custom_user.quarantine_room:
                    raise exceptions.ValidationException({'main': f'Member has code {code}: ' + messages.QUARANTINE_ROOM_EMPTY})
                self._members += [user]

    def extra_validate_to_refuse_member(self):
        if hasattr(self, '_member_codes'):
            self._member_codes = split_input_list(self._member_codes)
            self._members = []
            for code in self._member_codes:
                user = self.get_user_by_code(code)
                if not user:
                    raise exceptions.NotFoundException({'main': messages.MEMBER_NOT_FOUND})
                self._members += [user]

    def extra_validate_to_filter_member(self):
        self._role_name = 'MEMBER'
        if hasattr(self, '_created_at_max'):
            validators.DateStringValidator.valid(self._created_at_max, message={'created_at_max': messages.INVALID})
            self._created_at_max = date_string_to_timestamp(self._created_at_max, 1)
        if hasattr(self, '_created_at_min'):
            validators.DateStringValidator.valid(self._created_at_min, message={'created_at_min': messages.INVALID})
            self._created_at_min = date_string_to_timestamp(self._created_at_min, 0)
        if hasattr(self, '_positive_test'):
            if (self._positive_test):
                self._positive_test = 'true'
            else:
                self._positive_test = 'false'
        if hasattr(self, '_is_last_tested') and self._is_last_tested:
            test_day = int(os.environ.get('TEST_DAY_DEFAULT', 5))
            self._last_tested_max = str(datetime.datetime.now() - datetime.timedelta(days=test_day))
        if hasattr(self, '_can_finish_quarantine'):
            if self._can_finish_quarantine:
                self._positive_test = 'false'
                self._health_status_list = HealthStatus.NORMAL
                quarantine_day = int(os.environ.get('QUARANTINE_DAY_DEFAULT', 14))
                self._quarantined_at_max = datetime.datetime.now() - datetime.timedelta(days=quarantine_day)
                self._quarantined_at_max = timestamp_string_to_date_string(str(self._quarantined_at_max))
