import os
import datetime
from django.db.models import Q
from django.utils import timezone
from ..models import CustomUser, Member
from address.models import Country, City, District, Ward
from role.models import Role
from quarantine_ward.models import QuarantineWard, QuarantineRoom, QuarantineBuilding, QuarantineFloor
from form.models import BackgroundDisease, Pandemic
from utils import validators, messages, exceptions
from utils.enums import Gender, MemberLabel, CustomUserStatus, HealthStatus, MemberQuarantinedStatus, Professional
from utils.tools import split_input_list, is_change_date_in_time_zone_vn

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

    def is_validate_passport_number(self):
        if hasattr(self, '_passport_number'):
            self._passport_number = validators.PassportValidator.valid(
                value=self._passport_number,
            )

    def is_validate_health_insurance_number(self):
        if hasattr(self, '_health_insurance_number'):
            self._health_insurance_number = validators.HealthInsuranceNumberValidator.valid(
                value=self._health_insurance_number,
            )

    def is_validate_identity_number(self):
        if hasattr(self, '_identity_number'):
            self._identity_number = validators.IdentityNumberValidator.valid(
                value=self._identity_number,
            )

    def is_validate_professional(self):
        if hasattr(self, '_professional'):
            if self._professional:
                self._professional = validators.EnumValidator.valid(
                    value=self._professional,
                    enum_cls=Professional,
                    message={'professional': messages.INVALID},
                )
            else:
                self._professional = None

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

    def is_validate_status_list(self):
        if hasattr(self, '_status_list'):
            self._status_list = split_input_list(self._status_list)
            new_status_list = ''
            for item in self._status_list:
                new_status_list += ',' + validators.EnumValidator.valid(
                    value=item,
                    enum_cls=CustomUserStatus,
                    message={'status_list': messages.INVALID},
                )
            if new_status_list:
                new_status_list = new_status_list[1:]
            self._status_list = new_status_list

    def is_validate_quarantined_status_list(self):
        if hasattr(self, '_quarantined_status_list'):
            self._quarantined_status_list = split_input_list(self._quarantined_status_list)
            new_quarantined_status_list = ''
            for item in self._quarantined_status_list:
                new_quarantined_status_list += ',' + validators.EnumValidator.valid(
                    value=item,
                    enum_cls=MemberQuarantinedStatus,
                    message={'quarantined_status_list': messages.INVALID},
                )
            if new_quarantined_status_list:
                new_quarantined_status_list = new_quarantined_status_list[1:]
            self._quarantined_status_list = new_quarantined_status_list

    def is_validate_positive_test_now(self):
        if hasattr(self, '_positive_test_now') and self._positive_test_now != None:
            try:
                self._positive_test_now = validators.BooleanValidator.valid(
                    value=self._positive_test_now,
                )
            except:
                if self._positive_test_now == 'Null':
                    self._positive_test_now = None
                else:
                    raise exceptions.ValidationException({'positive_test_now': messages.INVALID})

    def is_validate_positive_test_now_list(self):
        if hasattr(self, '_positive_test_now_list'):
            self._positive_test_now_list = split_input_list(self._positive_test_now_list)
            new_positive_test_now_list = []
            for item in self._positive_test_now_list:
                try:
                    new_positive_test_now_list += [validators.BooleanValidator.valid(
                        value=item,
                    )]
                except Exception as exception:
                    if item == 'Null':
                        new_positive_test_now_list += [None]
                    else:
                        raise exceptions.ValidationException({'positive_test_now_list': messages.INVALID})
            self._positive_test_now_list = new_positive_test_now_list

    def is_validate_health_status_list(self):
        if hasattr(self, '_health_status_list'):
            self._health_status_list = split_input_list(self._health_status_list)
            new_health_status_list = ''
            for item in self._health_status_list:
                try:
                    new_health_status_list += validators.EnumValidator.valid(
                        value=item,
                        enum_cls=HealthStatus,
                    ) + ','
                except Exception as exception:
                    if item == 'Null':
                        new_health_status_list += item + ','
                    else:
                        raise exceptions.ValidationException({'health_status_list': messages.INVALID})
            if new_health_status_list:
                new_health_status_list = new_health_status_list[:-1]
            self._health_status_list = new_health_status_list

    def is_validate_role_name_list(self):
        if hasattr(self, '_role_name_list'):
            self._new_role_name_list = split_input_list(self._role_name_list)
            self._role_name_object_list = []
            for item in self._new_role_name_list:
                try:
                    object = validators.ModelInstanceExistenceValidator.valid(
                        model_cls=Role,
                        query_expr=Q(name=item),
                    )
                    self._role_name_object_list += [object]
                except Exception as exception:
                    raise exceptions.NotFoundException({f'role_name {item}': messages.NOT_EXIST})

    def is_validate_label_list(self):
        if hasattr(self, '_label_list'):
            new_label_list = split_input_list(self._label_list)
            for item in new_label_list:
                validators.EnumValidator.valid(
                    value=item,
                    enum_cls=MemberLabel,
                    message={'label_list': messages.INVALID},
                )

    def is_validate_is_last_tested(self):
        if hasattr(self, '_is_last_tested'):
            self._is_last_tested = validators.BooleanValidator.valid(
                value=self._is_last_tested,
                message={'is_last_tested': messages.INVALID},
            )

    def is_validate_first_positive_test_date(self):
        if hasattr(self, '_first_positive_test_date'):
            if self._first_positive_test_date:
                self._first_positive_test_date = validators.DateTimeFieldValidator.valid(
                    value=self._first_positive_test_date,
                    message={'first_positive_test_date': messages.INVALID_DATETIME},
                )
            else:
                self._first_positive_test_date = None

    def is_validate_quarantined_at(self):
        if hasattr(self, '_quarantined_at') and self._quarantined_at != None:
            self._quarantined_at = validators.DateTimeFieldValidator.valid(
                value=self._quarantined_at,
                message={'quarantined_at': messages.INVALID_DATETIME},
            )

    def is_validate_quarantined_at_max(self):
        if hasattr(self, '_quarantined_at_max'):
            self._quarantined_at_max = validators.DateTimeFieldValidator.valid(
                value=self._quarantined_at_max,
                message={'quarantined_at_max': messages.INVALID_DATETIME},
            )

    def is_validate_quarantined_at_min(self):
        if hasattr(self, '_quarantined_at_min'):
            self._quarantined_at_min = validators.DateTimeFieldValidator.valid(
                value=self._quarantined_at_min,
                message={'quarantined_at_min': messages.INVALID_DATETIME},
            )

    def is_validate_quarantined_finish_expected_at(self):
        if hasattr(self, '_quarantined_finish_expected_at') and self._quarantined_finish_expected_at != None:
            self._quarantined_finish_expected_at = validators.DateTimeFieldValidator.valid(
                value=self._quarantined_finish_expected_at,
                message={'quarantined_finish_expected_at': messages.INVALID_DATETIME},
            )

    def is_validate_quarantined_finish_expected_at_max(self):
        if hasattr(self, '_quarantined_finish_expected_at_max'):
            self._quarantined_finish_expected_at_max = validators.DateTimeFieldValidator.valid(
                value=self._quarantined_finish_expected_at_max,
                message={'quarantined_finish_expected_at_max': messages.INVALID_DATETIME},
            )

    def is_validate_quarantined_finish_expected_at_min(self):
        if hasattr(self, '_quarantined_finish_expected_at_min'):
            self._quarantined_finish_expected_at_min = validators.DateTimeFieldValidator.valid(
                value=self._quarantined_finish_expected_at_min,
                message={'quarantined_finish_expected_at_min': messages.INVALID_DATETIME},
            )

    def is_validate_created_at_max(self):
        if hasattr(self, '_created_at_max'):
            self._created_at_max = validators.DateTimeFieldValidator.valid(
                value=self._created_at_max,
                message={'created_at_max': messages.INVALID_DATETIME},
            )

    def is_validate_created_at_min(self):
        if hasattr(self, '_created_at_min'):
            self._created_at_min = validators.DateTimeFieldValidator.valid(
                value=self._created_at_min,
                message={'created_at_min': messages.INVALID_DATETIME},
            )

    def is_validate_order_by(self):
        if hasattr(self, '_order_by'):
            if self._order_by not in ['quarantined_finished_at', '-quarantined_finished_at']:
                raise exceptions.ValidationException({'order_by': messages.INVALID})

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
    
    def is_validate_is_need_change_room_because_be_positive(self):
        if hasattr(self, '_is_need_change_room_because_be_positive') and self._is_need_change_room_because_be_positive:
            self._is_need_change_room_because_be_positive = validators.BooleanValidator.valid(
                self._is_need_change_room_because_be_positive,
                message={'is_need_change_room_because_be_positive': messages.INVALID},
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

    def is_validate_care_area(self):
        if hasattr(self, '_care_area'):
            self._list_quarantine_floor_objects = []
            self._list_quarantine_floor_ids = split_input_list(self._care_area)
            for id in self._list_quarantine_floor_ids:
                try:
                    object = validators.ModelInstanceExistenceValidator.valid(
                        model_cls=QuarantineFloor,
                        query_expr=Q(id=id),
                    )
                    self._list_quarantine_floor_objects += [object]
                except Exception as exception:
                    raise exceptions.NotFoundException({'care_area': messages.NOT_EXIST})

    def is_validate_abroad(self):
        if hasattr(self, '_abroad'):
            self._abroad = validators.BooleanValidator.valid(
                self._abroad,
                message={'abroad': messages.INVALID},
            )

    def is_validate_number_of_vaccine_doses(self):
        if hasattr(self, '_number_of_vaccine_doses'):
            if self._number_of_vaccine_doses:
                self._number_of_vaccine_doses = validators.PositiveIntegerValidator.valid(
                    self._number_of_vaccine_doses,
                    message={'number_of_vaccine_doses': messages.INVALID},
                    message1={'number_of_vaccine_doses': messages.INVALID},
                )
            else:
                self._number_of_vaccine_doses = 0

    def is_validate_not_quarantine_room_ids(self):
        if hasattr(self, '_not_quarantine_room_ids'):
            self._not_quarantine_room_ids = split_input_list(self._not_quarantine_room_ids)
            for id in self._not_quarantine_room_ids:
                try:
                    validators.ModelInstanceExistenceValidator.valid(
                        model_cls=QuarantineRoom,
                        query_expr=Q(id=id),
                    )
                except Exception as exception:
                    raise exceptions.NotFoundException({'not_quarantine_room_ids': messages.NOT_EXIST})

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

    def is_custom_user_code_exist(self):
        if hasattr(self, '_custom_user_code'):
            try:
                self._custom_user = validators.ModelInstanceExistenceValidator.valid(
                    model_cls=CustomUser,
                    query_expr=Q(code=self._custom_user_code),
                )
                return True
            except Exception as exception:
                return False
        return False

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

    def check_country_ward_relationship(self):
        if hasattr(self, '_ward'):
            if not hasattr(self, '_district'):
                self._district = self._ward.district
                self._district_id = self._ward.district.id
            else:
                if self._district != self._ward.district:
                    raise exceptions.ValidationException({'country_ward_relationship': messages.INVALID})
            # print('ward ' + str(self._ward_id))
        
        if hasattr(self, '_district'):
            if not hasattr(self, '_city'):
                self._city = self._district.city
                self._city_id = self._district.city.id
            else:
                if self._city != self._district.city:
                    raise exceptions.ValidationException({'country_ward_relationship': messages.INVALID})
            # print('district ' + str(self._district_id))

        if hasattr(self, '_city'):
            if not hasattr(self, '_country'):
                self._country = self._city.country
                self._country_code = self._city.country.code
            else:
                if self._country != self._city.country:
                    raise exceptions.ValidationException({'country_ward_relationship': messages.INVALID})
            # print('city ' + str(self._city_id))
        
        # if hasattr(self, '_country'):
        #     print('country ' + str(self._country_code))

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

    def is_quarantine_building_id_exist(self):
        if hasattr(self, '_quarantine_building_id'):
            try:
                self._quarantine_building = validators.ModelInstanceExistenceValidator.valid(
                    model_cls=QuarantineBuilding,
                    query_expr=Q(id=self._quarantine_building_id),
                )
                return True
            except Exception as exception:
                return False
        return True

    def is_quarantine_floor_id_exist(self, id=None):
        if id:
            try:
                validators.ModelInstanceExistenceValidator.valid(
                    model_cls=QuarantineFloor,
                    query_expr=Q(id=id),
                )
                return True
            except Exception as exception:
                return False
        elif hasattr(self, '_quarantine_floor_id'):
            try:
                self._quarantine_floor = validators.ModelInstanceExistenceValidator.valid(
                    model_cls=QuarantineFloor,
                    query_expr=Q(id=self._quarantine_floor_id),
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

    def check_quarantine_ward_room_relationship(self):
        if hasattr(self, '_quarantine_room'):
            if not hasattr(self, '_quarantine_floor'):
                self._quarantine_floor = self._quarantine_room.quarantine_floor
                self._quarantine_floor_id = self._quarantine_room.quarantine_floor.id
            else:
                if self._quarantine_floor != self._quarantine_room.quarantine_floor:
                    raise exceptions.ValidationException({'quarantine_ward_room_relationship': messages.INVALID})
            # print('room ' + str(self._quarantine_room_id))
        
        if hasattr(self, '_quarantine_floor'):
            if not hasattr(self, '_quarantine_building'):
                self._quarantine_building = self._quarantine_floor.quarantine_building
                self._quarantine_building_id = self._quarantine_floor.quarantine_building.id
            else:
                if self._quarantine_building != self._quarantine_floor.quarantine_building:
                    raise exceptions.ValidationException({'quarantine_ward_room_relationship': messages.INVALID})
            # print('floor ' + str(self._quarantine_floor_id))

        if hasattr(self, '_quarantine_building'):
            if not hasattr(self, '_quarantine_ward'):
                self._quarantine_ward = self._quarantine_building.quarantine_ward
                self._quarantine_ward_id = self._quarantine_building.quarantine_ward.id
            else:
                if self._quarantine_ward != self._quarantine_building.quarantine_ward:
                    raise exceptions.ValidationException({'quarantine_ward_room_relationship': messages.INVALID})
            # print('building ' + str(self._quarantine_building_id))
        
        # if hasattr(self, '_quarantine_ward'):
        #     print('ward ' + str(self._quarantine_ward_id))

    def is_care_staff_code_exist(self):
        if hasattr(self, '_care_staff_code'):
            try:
                self._care_staff = validators.ModelInstanceExistenceValidator.valid(
                    model_cls=CustomUser,
                    query_expr=Q(code=self._care_staff_code),
                )
                return True
            except Exception as exception:
                return False
        return True

    def extra_validate_to_get_user_by_phone_number(self):
        if hasattr(self, '_phone_number') and self._phone_number:
            if not self.is_phone_number_exist():
                raise exceptions.ValidationException({'phone_number': messages.NOT_EXIST})

    def extra_validate_to_get_member_timeline(self):
        if hasattr(self, '_code'):
            if not self.is_code_exist():
                raise exceptions.ValidationException({'code': messages.NOT_EXIST})
        if self._custom_user.role.name != 'MEMBER' or not hasattr(self._custom_user, 'member_x_custom_user'):
            raise exceptions.ValidationException({'code': messages.ISNOTMEMBER})
        if self._custom_user.status not in [CustomUserStatus.AVAILABLE, CustomUserStatus.LEAVE]:
            raise exceptions.ValidationException({'code': messages.IS_NOT_AVAILABLE_OR_LEAVE})

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
        self.check_country_ward_relationship()
        if hasattr(self, '_quarantine_ward_id') and not self.is_quarantine_ward_id_exist():
            raise exceptions.NotFoundException({'quarantine_ward_id': messages.NOT_EXIST})
        if hasattr(self, '_quarantine_room_id'):
            if self._quarantine_room_id and not self.is_quarantine_room_id_exist():
                raise exceptions.NotFoundException({'quarantine_room_id': messages.NOT_EXIST})
        if not hasattr(self, '_number_of_vaccine_doses'):
            self._number_of_vaccine_doses = 0
        if hasattr(self, '_quarantined_at') and self._quarantined_at:
            ...
        else:
            self._quarantined_at = timezone.now()

        # Also set quarantined_finish_expected_at
        if self._quarantine_ward.pandemic:
            if self._number_of_vaccine_doses < 2:
                remain_qt = self._quarantine_ward.pandemic.quarantine_time_not_vac
            else:
                remain_qt = self._quarantine_ward.pandemic.quarantine_time_vac
        else:
            if self._number_of_vaccine_doses < 2:
                remain_qt = int(os.environ.get('QUARANTINE_TIME_NOT_VAC', 14))
            else:
                remain_qt = int(os.environ.get('QUARANTINE_TIME_VAC', 10))
        self._quarantined_finish_expected_at = self._quarantined_at + datetime.timedelta(days=remain_qt)

        if hasattr(self, '_label') and self._label == MemberLabel.F0:
            self._positive_test_now = True
            if self._quarantine_ward.pandemic:
                if self._number_of_vaccine_doses < 2:
                    remain_qt = self._quarantine_ward.pandemic.remain_qt_pos_not_vac
                else:
                    remain_qt = self._quarantine_ward.pandemic.remain_qt_pos_vac
            else:
                if self._number_of_vaccine_doses < 2:
                    remain_qt = int(os.environ.get('REMAIN_QT_POS_NOT_VAC', 14))
                else:
                    remain_qt = int(os.environ.get('REMAIN_QT_POS_VAC', 10))
            self._quarantined_finish_expected_at = self._quarantined_at + datetime.timedelta(days=remain_qt)

        if hasattr(self, '_first_positive_test_date'):
            if self._first_positive_test_date:
                if (not hasattr(self, '_positive_tested_before') or self._positive_tested_before == False) \
                and (not hasattr(self, '_label') or self._label != MemberLabel.F0):
                    raise exceptions.ValidationException({'first_positive_test_date': messages.MUST_EMPTY})

        if hasattr(self, '_care_staff_code') and self._care_staff_code:
            if not self.is_care_staff_code_exist():
                raise exceptions.NotFoundException({'care_staff_code': messages.NOT_EXIST})
            if self._care_staff.role.name != 'STAFF':
                raise exceptions.ValidationException({'care_staff_code': messages.ISNOTSTAFF})
            if self._care_staff.status != CustomUserStatus.AVAILABLE:
                raise exceptions.ValidationException({'care_staff_code': messages.NOT_AVAILABLE})
            if self._care_staff.quarantine_ward != self._quarantine_ward:
                raise exceptions.ValidationException({'care_staff_code': messages.NOT_IN_QUARANTINE_WARD_OF_MEMBER})

    def extra_validate_to_create_manager(self):
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
        self.check_country_ward_relationship()
        if hasattr(self, '_quarantine_ward_id') and not self.is_quarantine_ward_id_exist():
            raise exceptions.NotFoundException({'quarantine_ward_id': messages.NOT_EXIST})

    def extra_validate_to_create_staff(self):
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
        self.check_country_ward_relationship()
        if hasattr(self, '_quarantine_ward_id') and not self.is_quarantine_ward_id_exist():
            raise exceptions.NotFoundException({'quarantine_ward_id': messages.NOT_EXIST})

    def extra_validate_to_update_member(self, sender):
        if hasattr(self, '_code') and not self.is_code_exist():
            raise exceptions.NotFoundException({'code': messages.NOT_EXIST})
        if hasattr(self, '_custom_user'):
            if self._custom_user.role.name != 'MEMBER' or not hasattr(self._custom_user, 'member_x_custom_user'):
                raise exceptions.ValidationException({'main': messages.ISNOTMEMBER})
        if hasattr(self, '_email') and not self.is_new_email_valid():
            raise exceptions.NotFoundException({'email': messages.EXIST})
        if hasattr(self, '_health_insurance_number') and not self.is_new_health_insurance_number_valid():
            raise exceptions.NotFoundException({'health_insurance_number': messages.EXIST})
        if hasattr(self, '_identity_number'):
            if not self._identity_number:
                raise exceptions.ValidationException({'identity_number': messages.EMPTY})
            elif self._custom_user.identity_number and sender.role.name in ['STAFF', 'MEMBER'] and self._custom_user.identity_number != self._identity_number:
                raise exceptions.AuthenticationException({'identity_number': messages.CANNOT_CHANGE})
            elif not self.is_new_identity_number_valid():
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
        self.check_country_ward_relationship()
        if hasattr(self, '_quarantine_ward_id'):
            if self._quarantine_ward_id:
                if not self.is_quarantine_ward_id_exist():
                    raise exceptions.NotFoundException({'quarantine_ward_id': messages.NOT_EXIST})
                if self._custom_user.status == CustomUserStatus.AVAILABLE:
                    if self._custom_user.quarantine_ward != self._quarantine_ward:
                        raise exceptions.ValidationException({'quarantine_ward_id': messages.CANNOT_CHANGE})
            else:
                raise exceptions.ValidationException({'quarantine_ward_id': messages.EMPTY})
        if hasattr(self, '_quarantine_room_id'):
            if self._custom_user.status == CustomUserStatus.AVAILABLE:
                if not self._quarantine_room_id:
                    raise exceptions.NotFoundException({'quarantine_room_id': messages.EMPTY})
                if not self.is_quarantine_room_id_exist():
                    raise exceptions.NotFoundException({'quarantine_room_id': messages.NOT_EXIST})
            elif self._custom_user.status in [CustomUserStatus.REFUSED, CustomUserStatus.WAITING, CustomUserStatus.LEAVE]:
                if self._quarantine_room_id:
                    raise exceptions.NotFoundException({'quarantine_room_id': messages.MUST_EMPTY})
        if hasattr(self, '_quarantined_at'):
            if not self._quarantined_at:
                if self._custom_user.status in [CustomUserStatus.AVAILABLE, CustomUserStatus.LEAVE]:
                    raise exceptions.ValidationException({'quarantined_at': messages.EMPTY})
            else:
                if self._custom_user.status not in [CustomUserStatus.AVAILABLE, CustomUserStatus.LEAVE]:
                    raise exceptions.ValidationException({'quarantined_at': messages.MUST_EMPTY})

                if is_change_date_in_time_zone_vn(self._quarantined_at, self._custom_user.member_x_custom_user.quarantined_at):
                    if sender.role.name == 'MEMBER':
                        raise exceptions.AuthenticationException({'quarantined_at': messages.NO_PERMISSION})

                    old_quarantined_finish_expected_at = self._custom_user.member_x_custom_user.quarantined_finish_expected_at
                    if not hasattr(self, '_quarantined_finish_expected_at') or not is_change_date_in_time_zone_vn(self._quarantined_finish_expected_at, old_quarantined_finish_expected_at):
                        # also update quarantined_finish_expected_at
                        if hasattr(self, '_quarantine_ward'):
                            quarantine_ward = self._quarantine_ward
                        else:
                            quarantine_ward = self._custom_user.quarantine_ward
                        number_of_vaccine_doses = self._custom_user.member_x_custom_user.number_of_vaccine_doses
                        if quarantine_ward.pandemic:
                            if number_of_vaccine_doses < 2:
                                remain_qt = quarantine_ward.pandemic.quarantine_time_not_vac
                            else:
                                remain_qt = quarantine_ward.pandemic.quarantine_time_vac
                        else:
                            if number_of_vaccine_doses < 2:
                                remain_qt = int(os.environ.get('QUARANTINE_TIME_NOT_VAC', 14))
                            else:
                                remain_qt = int(os.environ.get('QUARANTINE_TIME_VAC', 10))

                        new_quarantined_finish_expected_at = self._quarantined_at + datetime.timedelta(days=remain_qt)
                        if old_quarantined_finish_expected_at and old_quarantined_finish_expected_at < new_quarantined_finish_expected_at:
                            self._quarantined_finish_expected_at = new_quarantined_finish_expected_at
        if hasattr(self, '_quarantined_finish_expected_at'):
            if is_change_date_in_time_zone_vn(self._quarantined_finish_expected_at, self._custom_user.member_x_custom_user.quarantined_finish_expected_at):
                if sender.role.name == 'MEMBER':
                    raise exceptions.AuthenticationException({'quarantined_finish_expected_at': messages.NO_PERMISSION})
                if self._quarantined_finish_expected_at:
                    if self._custom_user.status not in [CustomUserStatus.AVAILABLE, CustomUserStatus.LEAVE]:
                        raise exceptions.ValidationException({'quarantined_finish_expected_at': messages.MUST_EMPTY})

        if hasattr(self, '_label') and self._label != self._custom_user.member_x_custom_user.label:
            if hasattr(self, '_quarantine_room') and self._quarantine_room != self._custom_user.member_x_custom_user.quarantine_room:
                raise exceptions.ValidationException({'main': messages.CANNOT_CHANGE_ROOM_LABEL_TOGETHER})

        if hasattr(self, '_first_positive_test_date') and is_change_date_in_time_zone_vn(self._first_positive_test_date, self._custom_user.member_x_custom_user.first_positive_test_date):
            if self._custom_user.status not in [CustomUserStatus.WAITING, CustomUserStatus.REFUSED]:
                raise exceptions.ValidationException({'first_positive_test_date': messages.CANNOT_CHANGE})
            elif self._first_positive_test_date:
                label_to_check = self._label if hasattr(self, '_label') else self._custom_user.member_x_custom_user.label
                positive_tested_before_to_check = self._positive_tested_before if hasattr(self, '_positive_tested_before') else self._custom_user.member_x_custom_user.positive_tested_before
                if label_to_check != MemberLabel.F0 and positive_tested_before_to_check == False:
                    raise exceptions.ValidationException({'first_positive_test_date': messages.MUST_EMPTY})

        if hasattr(self, '_care_staff_code'):
            if self._care_staff_code:
                if not self.is_care_staff_code_exist():
                    raise exceptions.NotFoundException({'care_staff_code': messages.NOT_EXIST})
                if self._care_staff.role.name != 'STAFF':
                    raise exceptions.ValidationException({'care_staff_code': messages.ISNOTSTAFF})
                if self._care_staff.status != CustomUserStatus.AVAILABLE:
                    raise exceptions.ValidationException({'care_staff_code': messages.NOT_AVAILABLE})
                if self._care_staff.quarantine_ward != (self._quarantine_ward if hasattr(self, '_quarantine_ward') else self._custom_user.quarantine_ward):
                    raise exceptions.ValidationException({'care_staff_code': messages.NOT_IN_QUARANTINE_WARD_OF_MEMBER})
            else:
                self._care_staff = None

    def extra_validate_to_update_manager(self):
        if hasattr(self, '_code') and not self.is_code_exist():
            raise exceptions.NotFoundException({'code': messages.NOT_EXIST})
        if hasattr(self, '_custom_user'):
            if self._custom_user.role.name not in ['SUPER_MANAGER', 'MANAGER']:
                raise exceptions.ValidationException({'main': messages.ISNOTMANAGER})
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
        self.check_country_ward_relationship()
        if hasattr(self, '_quarantine_ward_id') and not self.is_quarantine_ward_id_exist():
            raise exceptions.NotFoundException({'quarantine_ward_id': messages.NOT_EXIST})

    def extra_validate_to_update_staff(self):
        if hasattr(self, '_code') and not self.is_code_exist():
            raise exceptions.NotFoundException({'code': messages.NOT_EXIST})
        if hasattr(self, '_custom_user'):
            if self._custom_user.role.name != 'STAFF':
                raise exceptions.ValidationException({'main': messages.ISNOTSTAFF})
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
        self.check_country_ward_relationship()
        if hasattr(self, '_quarantine_ward_id') and not self.is_quarantine_ward_id_exist():
            raise exceptions.NotFoundException({'quarantine_ward_id': messages.NOT_EXIST})

    def extra_validate_to_accept_one_member(self):
        if hasattr(self, '_code') and not self.is_code_exist():
            raise exceptions.NotFoundException({'main': messages.MEMBER_NOT_FOUND})
        if hasattr(self, '_quarantine_room_id') and self._quarantine_room_id:
            if not self.is_quarantine_room_id_exist():
                raise exceptions.NotFoundException({'quarantine_room_id': messages.NOT_EXIST})
        else:
            self._quarantine_room = None
        if hasattr(self, '_care_staff_code') and self._care_staff_code:
            if not self.is_care_staff_code_exist():
                raise exceptions.NotFoundException({'care_staff_code': messages.NOT_EXIST})
            if self._care_staff.role.name != 'STAFF':
                raise exceptions.ValidationException({'care_staff_code': messages.ISNOTSTAFF})
            if self._care_staff.status != CustomUserStatus.AVAILABLE:
                raise exceptions.ValidationException({'care_staff_code': messages.NOT_AVAILABLE})
        else:
            self._care_staff = None

    def extra_validate_to_accept_many_members(self):
        if hasattr(self, '_member_codes'):
            self._member_codes = split_input_list(self._member_codes)
            self._members = []
            for code in self._member_codes:
                user = self.get_user_by_code(code)
                if not user:
                    raise exceptions.NotFoundException({'main': f'{code}: ' + messages.MEMBER_NOT_FOUND})
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

    def check_member_can_finish_quarantine(self, custom_user):
        if custom_user.member_x_custom_user.positive_test_now != False:
            return False
        if custom_user.member_x_custom_user.quarantined_finish_expected_at > timezone.now():
            return False
        if custom_user.member_x_custom_user.health_status in [HealthStatus.SERIOUS]:
            return False
        return True

    def extra_validate_to_finish_quarantine_member(self):
        if hasattr(self, '_member_codes'):
            self._member_codes = split_input_list(self._member_codes)
            self._members = []
            for code in self._member_codes:
                user = self.get_user_by_code(code)
                if not user:
                    raise exceptions.NotFoundException({'main': f'{code}: ' + messages.MEMBER_NOT_FOUND})
                self._members += [user]

    def extra_validate_to_filter_member(self):
        self._role_name = 'MEMBER'
        if not hasattr(self, '_status_list'):
            self._status_list = CustomUserStatus.AVAILABLE
        if hasattr(self, '_quarantine_ward_id') and not self.is_quarantine_ward_id_exist():
            raise exceptions.NotFoundException({'quarantine_ward_id': messages.NOT_EXIST})
        if hasattr(self, '_quarantine_building_id') and not self.is_quarantine_building_id_exist():
            raise exceptions.NotFoundException({'quarantine_building_id': messages.NOT_EXIST})
        if hasattr(self, '_quarantine_floor_id') and not self.is_quarantine_floor_id_exist():
            raise exceptions.NotFoundException({'quarantine_floor_id': messages.NOT_EXIST})
        if hasattr(self, '_quarantine_room_id') and not self.is_quarantine_room_id_exist():
            raise exceptions.NotFoundException({'quarantine_room_id': messages.NOT_EXIST})
        self.check_quarantine_ward_room_relationship()
        if hasattr(self, '_care_staff_code') and not self.is_care_staff_code_exist():
            raise exceptions.NotFoundException({'care_staff_code': messages.NOT_EXIST})
        if hasattr(self, '_is_last_tested') and self._is_last_tested:
            try:
                pandemic = Pandemic.objects.get(name='Covid-19')
                day_between_tests = int(pandemic.day_between_tests)
            except:
                day_between_tests = int(os.environ.get('DAY_BETWEEN_TESTS', 5))
            self._last_tested_max = timezone.now() - datetime.timedelta(days=day_between_tests)
            self._status_list = CustomUserStatus.AVAILABLE
        if hasattr(self, '_can_finish_quarantine'):
            if self._can_finish_quarantine:
                self._status_list = CustomUserStatus.AVAILABLE
                self._positive_test_now_list = [False]
                self._health_status_list = f'{HealthStatus.NORMAL},{HealthStatus.UNWELL}'
                self._quarantined_finish_expected_at_max = timezone.now()
        if hasattr(self, '_is_need_change_room_because_be_positive') and self._is_need_change_room_because_be_positive == True:
            self._status_list = CustomUserStatus.AVAILABLE
            self._positive_test_now_list = [True]

    def extra_validate_to_filter_staff(self):
        self._role_name = 'STAFF'
        if not hasattr(self, '_status_list'):
            self._status_list = CustomUserStatus.AVAILABLE
        if hasattr(self, '_quarantine_ward_id') and not self.is_quarantine_ward_id_exist():
            raise exceptions.NotFoundException({'quarantine_ward_id': messages.NOT_EXIST})
        if hasattr(self, '_is_last_tested') and self._is_last_tested:
            test_day = int(os.environ.get('TEST_DAY_DEFAULT', 5))
            self._last_tested_max = timezone.now() - datetime.timedelta(days=test_day)

    def extra_validate_to_filter_manager(self):
        self._role_name_list = 'MANAGER,SUPER_MANAGER'
        if not hasattr(self, '_status_list'):
            self._status_list = CustomUserStatus.AVAILABLE
        if hasattr(self, '_quarantine_ward_id') and not self.is_quarantine_ward_id_exist():
            raise exceptions.NotFoundException({'quarantine_ward_id': messages.NOT_EXIST})
        if hasattr(self, '_is_last_tested') and self._is_last_tested:
            test_day = int(os.environ.get('TEST_DAY_DEFAULT', 5))
            self._last_tested_max = timezone.now() - datetime.timedelta(days=test_day)

    def extra_validate_to_filter_not_member(self):
        if not hasattr(self, '_status'):
            self._status = CustomUserStatus.AVAILABLE
        if hasattr(self, '_quarantine_ward_id') and not self.is_quarantine_ward_id_exist():
            raise exceptions.NotFoundException({'quarantine_ward_id': messages.NOT_EXIST})

    def extra_validate_to_get_suitable_room(self):
        if not hasattr(self, '_positive_test_now'):
            self._positive_test_now = None
        if hasattr(self, '_quarantine_ward_id') and not self.is_quarantine_ward_id_exist():
            raise exceptions.NotFoundException({'quarantine_ward_id': messages.NOT_EXIST})
        if hasattr(self, '_old_quarantine_room_id') and self._old_quarantine_room_id:
            self._quarantine_room_id = self._old_quarantine_room_id
            if not self.is_quarantine_room_id_exist():
                raise exceptions.NotFoundException({'old_quarantine_room_id': messages.NOT_EXIST})
            self._old_quarantine_room = self._quarantine_room
        else:
            self._old_quarantine_room = None
        if not hasattr(self, '_not_quarantine_room_ids'):
            self._not_quarantine_room_ids = []

    def extra_validate_to_change_quarantine_ward_and_room_of_available_member(self):
        if hasattr(self, '_custom_user_code') and not self.is_custom_user_code_exist():
            raise exceptions.NotFoundException({'main': messages.MEMBER_NOT_FOUND})
        if hasattr(self, '_quarantine_ward_id') and not self.is_quarantine_ward_id_exist():
            raise exceptions.NotFoundException({'quarantine_ward_id': messages.NOT_EXIST})
        if hasattr(self, '_quarantine_room_id') and self._quarantine_room_id:
            if not self.is_quarantine_room_id_exist():
                raise exceptions.NotFoundException({'quarantine_room_id': messages.NOT_EXIST})
        else:
            self._quarantine_room = None
        if hasattr(self, '_care_staff_code') and self._care_staff_code:
            if not self.is_care_staff_code_exist():
                raise exceptions.NotFoundException({'care_staff_code': messages.NOT_EXIST})
            if self._care_staff.role.name != 'STAFF':
                raise exceptions.ValidationException({'care_staff_code': messages.ISNOTSTAFF})
            if self._care_staff.status != CustomUserStatus.AVAILABLE:
                raise exceptions.ValidationException({'care_staff_code': messages.NOT_AVAILABLE})
        else:
            self._care_staff = None

    def extra_validate_to_hospitalize(self):
        if hasattr(self, '_code') and not self.is_code_exist():
            raise exceptions.NotFoundException({'code': messages.NOT_EXIST})
        if hasattr(self, '_custom_user') and self._custom_user:
            if self._custom_user.role.name != 'MEMBER' or not hasattr(self._custom_user, 'member_x_custom_user'):
                raise exceptions.ValidationException({'code': messages.ISNOTMEMBER})
            if self._custom_user.status != CustomUserStatus.AVAILABLE:
                raise exceptions.ValidationException({'code': messages.ISNOTAVAILABLE})
            if self._custom_user.member_x_custom_user.quarantined_status == MemberQuarantinedStatus.HOSPITALIZE_WAITING:
                raise exceptions.ValidationException({'code': messages.ALREADY_HOSPITALIZE_WAITING})

    def extra_validate_to_bvdc_call_hospitalize_confirm(self):
        if hasattr(self, '_confirm') and self._confirm not in ['ACCEPT', 'REFUSE']:
            raise exceptions.ValidationException({'confirm': messages.INVALID})
        if hasattr(self, '_phone_number') and not self.is_phone_number_exist():
            raise exceptions.NotFoundException({'phone_number': messages.NOT_EXIST})
        if hasattr(self, '_custom_user') and self._custom_user:
            if self._custom_user.role.name != 'MEMBER' or not hasattr(self._custom_user, 'member_x_custom_user'):
                raise exceptions.ValidationException({'phone_number': messages.ISNOTMEMBER})
            if not (self._custom_user.status == CustomUserStatus.AVAILABLE and self._custom_user.member_x_custom_user.quarantined_status == MemberQuarantinedStatus.HOSPITALIZE_WAITING):
                raise exceptions.ValidationException({'phone_number': messages.IS_NOT_HOSPITALIZE_WAITING})

    def extra_validate_to_member_call_requarantine(self, sender):
        if hasattr(self, '_quarantine_ward_id') and self._quarantine_ward_id:
            if not self.is_quarantine_ward_id_exist():
                raise exceptions.ValidationException({'quarantine_ward_id': messages.NOT_EXIST})
        if hasattr(self, '_first_positive_test_date'):
            if self._first_positive_test_date:
                label_to_check = self._label if hasattr(self, '_label') else sender.member_x_custom_user.label
                positive_tested_before_to_check = self._positive_tested_before if hasattr(self, '_positive_tested_before') else sender.member_x_custom_user.positive_tested_before
                if label_to_check != MemberLabel.F0 and positive_tested_before_to_check == False:
                    raise exceptions.ValidationException({'first_positive_test_date': messages.MUST_EMPTY})

    def extra_validate_to_manager_call_requarantine(self):
        if hasattr(self, '_code') and not self.is_code_exist():
            raise exceptions.NotFoundException({'code': messages.NOT_EXIST})
        if hasattr(self, '_custom_user'):
            if self._custom_user.role.name != 'MEMBER' or not hasattr(self._custom_user, 'member_x_custom_user'):
                raise exceptions.ValidationException({'code': messages.ISNOTMEMBER})
            if self._custom_user.status != CustomUserStatus.LEAVE:
                raise exceptions.ValidationException({'code': messages.ISNOTLEAVE})

        self._quarantined_status = MemberQuarantinedStatus.QUARANTINING

        if hasattr(self, '_quarantine_ward_id') and self._quarantine_ward_id:
            if not self.is_quarantine_ward_id_exist():
                raise exceptions.ValidationException({'quarantine_ward_id': messages.NOT_EXIST})
        if hasattr(self, '_quarantined_at') and self._quarantined_at:
            ...
        else:
            self._quarantined_at = timezone.now()

        # Also set quarantined_finish_expected_at
        if self._quarantine_ward.pandemic:
            if self._custom_user.member_x_custom_user.number_of_vaccine_doses < 2:
                remain_qt = self._quarantine_ward.pandemic.quarantine_time_not_vac
            else:
                remain_qt = self._quarantine_ward.pandemic.quarantine_time_vac
        else:
            if self._custom_user.member_x_custom_user.number_of_vaccine_doses < 2:
                remain_qt = int(os.environ.get('QUARANTINE_TIME_NOT_VAC', 14))
            else:
                remain_qt = int(os.environ.get('QUARANTINE_TIME_VAC', 10))
        self._quarantined_finish_expected_at = self._quarantined_at + datetime.timedelta(days=remain_qt)

        self._quarantined_finished_at = None

        if hasattr(self, '_label') and self._label == MemberLabel.F0:
            self._positive_test_now = True
            if self._quarantine_ward.pandemic:
                if self._custom_user.member_x_custom_user.number_of_vaccine_doses < 2:
                    remain_qt = self._quarantine_ward.pandemic.remain_qt_pos_not_vac
                else:
                    remain_qt = self._quarantine_ward.pandemic.remain_qt_pos_vac
            else:
                if self._custom_user.member_x_custom_user.number_of_vaccine_doses < 2:
                    remain_qt = int(os.environ.get('REMAIN_QT_POS_NOT_VAC', 14))
                else:
                    remain_qt = int(os.environ.get('REMAIN_QT_POS_VAC', 10))
            self._quarantined_finish_expected_at = self._quarantined_at + datetime.timedelta(days=remain_qt)
        else:
            self._positive_test_now = None

        if hasattr(self, '_first_positive_test_date'):
            if self._first_positive_test_date:
                label_to_check = self._label if hasattr(self, '_label') else self._custom_user.member_x_custom_user.label
                positive_tested_before_to_check = self._positive_tested_before if hasattr(self, '_positive_tested_before') else self._custom_user.member_x_custom_user.positive_tested_before
                if label_to_check != MemberLabel.F0 and positive_tested_before_to_check == False:
                    raise exceptions.ValidationException({'first_positive_test_date': messages.MUST_EMPTY})

        if not hasattr(self, '_quarantine_reason'):
            self._quarantine_reason = None

        if hasattr(self, '_quarantine_room_id') and self._quarantine_room_id:
            if not self.is_quarantine_room_id_exist():
                raise exceptions.NotFoundException({'quarantine_room_id': messages.NOT_EXIST})
        if hasattr(self, '_care_staff_code'):
            if self._care_staff_code:
                if not self.is_care_staff_code_exist():
                    raise exceptions.NotFoundException({'care_staff_code': messages.NOT_EXIST})
                if self._care_staff.role.name != 'STAFF':
                    raise exceptions.ValidationException({'care_staff_code': messages.ISNOTSTAFF})
                if self._care_staff.status != CustomUserStatus.AVAILABLE:
                    raise exceptions.ValidationException({'care_staff_code': messages.NOT_AVAILABLE})
                if self._care_staff.quarantine_ward != self._quarantine_ward:
                    raise exceptions.ValidationException({'care_staff_code': messages.NOT_IN_QUARANTINE_WARD_OF_MEMBER})
            else:
                self._care_staff = None