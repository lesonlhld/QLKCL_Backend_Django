import re
from django.db.models import Q
from ..models import Vaccine, VaccineDose
from user_account.models import CustomUser
from utils import validators, messages, exceptions

class VaccineValidator(validators.AbstractRequestValidate):

    def is_valid_fields(self, keys: list):
        ignorable_fields = {}
        set_of_keys = set(keys)

        return super().is_valid_fields(set_of_keys)

    def is_id_exist(self):
        if hasattr(self, '_id'):
            try:
                self._vaccine = validators.ModelInstanceExistenceValidator.valid(
                    model_cls=Vaccine,
                    query_expr=Q(id=self._id),
                )
                return True
            except Exception as exception:
                return False
        return False

    def is_name_manufacturer_exist(self):
        if hasattr(self, '_name') and hasattr(self, '_manufacturer'):
            try:
                validators.ModelInstanceExistenceValidator.valid(
                    model_cls=Vaccine,
                    query_expr=Q(name=self._name, manufacturer=self._manufacturer),
                )
                return True
            except Exception as exception:
                return False
        return False

    def get_vaccine_by_name_manufacturer(self, name, manufacturer):
        try:
            return validators.ModelInstanceExistenceValidator.valid(
                model_cls=Vaccine,
                query_expr=Q(name=name, manufacturer=manufacturer),
            )
        except Exception as exception:
            return None

    def extra_validate_to_get_vaccine(self):
        if hasattr(self, '_id') and not self.is_id_exist():
            raise exceptions.ValidationException({'id': messages.NOT_EXIST}) 

    def extra_validate_to_create_vaccine(self):
        if self.is_name_manufacturer_exist():
            raise exceptions.ValidationException({'name,manufacturer': messages.EXIST})

    def extra_validate_to_update_vaccine(self):
        if hasattr(self, '_id') and not self.is_id_exist():
            raise exceptions.ValidationException({'id': messages.NOT_EXIST})
        if hasattr(self, '_name') or hasattr(self, '_manufacturer'):
            if hasattr(self, '_name'):
                if not self._name:
                    raise exceptions.ValidationException({'name': messages.EMPTY})
            else:
                self._name = self._vaccine.name
            if hasattr(self, '_manufacturer'):
                if not self._manufacturer:
                    raise exceptions.ValidationException({'manufacturer': messages.EMPTY})
            else:
                self._manufacturer = self._vaccine.manufacturer
            # check if exist vaccine with same name and manufacturer
            vaccine = self.get_vaccine_by_name_manufacturer(self._name, self._manufacturer)
            if vaccine and vaccine != self._vaccine:
                raise exceptions.ValidationException({'name,manufacturer': messages.EXIST})

class VaccineDoseValidator(validators.AbstractRequestValidate):

    def is_valid_fields(self, keys: list):
        ignorable_fields = {}
        set_of_keys = set(keys)

        return super().is_valid_fields(set_of_keys)

    def get_vaccine_dose_by_vaccine_custom_user_injection_date(self, vaccine, custom_user, injection_date):
        if vaccine and custom_user and injection_date:
            try:
                return validators.ModelInstanceExistenceValidator.valid(
                    model_cls=VaccineDose,
                    query_expr=Q(vaccine=vaccine, custom_user=custom_user, injection_date=injection_date),
                )
            except Exception as exception:
                return None
        return None

    def is_validate_injection_date(self):
        if hasattr(self, '_injection_date'):
            if self._injection_date:
                self._injection_date = validators.DateTimeFieldValidator.valid(
                    value=self._injection_date,
                    message={'injection_date': messages.INVALID_DATETIME},
                )
            else:
                raise exceptions.ValidationException({'injection_date': messages.EMPTY})

    def is_validate_injection_date_max(self):
        if hasattr(self, '_injection_date_max'):
            if self._injection_date_max:
                self._injection_date_max = validators.DateTimeFieldValidator.valid(
                    value=self._injection_date_max,
                    message={'injection_date_max': messages.INVALID_DATETIME},
                )
            else:
                raise exceptions.ValidationException({'injection_date_max': messages.EMPTY})

    def is_validate_injection_date_min(self):
        if hasattr(self, '_injection_date_min'):
            if self._injection_date_min:
                self._injection_date_min = validators.DateTimeFieldValidator.valid(
                    value=self._injection_date_min,
                    message={'injection_date_min': messages.INVALID_DATETIME},
                )
            else:
                raise exceptions.ValidationException({'injection_date_min': messages.EMPTY})

    def is_id_exist(self):
        if hasattr(self, '_id'):
            try:
                self._vaccine_dose = validators.ModelInstanceExistenceValidator.valid(
                    model_cls=VaccineDose,
                    query_expr=Q(id=self._id),
                )
                return True
            except Exception as exception:
                return False
        return False

    def is_vaccine_id_exist(self):
        if hasattr(self, '_vaccine_id'):
            try:
                self._vaccine = validators.ModelInstanceExistenceValidator.valid(
                    model_cls=Vaccine,
                    query_expr=Q(id=self._vaccine_id),
                )
                return True
            except Exception as exception:
                return False
        return False

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

    def is_vaccine_custom_user_injection_date_exist(self):
        if hasattr(self, '_vaccine') and hasattr(self, '_custom_user') and hasattr(self, '_injection_date'):
            try:
                validators.ModelInstanceExistenceValidator.valid(
                    model_cls=VaccineDose,
                    query_expr=Q(vaccine=self._vaccine, custom_user=self._custom_user, injection_date=self._injection_date),
                )
                return True
            except Exception as exception:
                return False
        return False

    def extra_validate_to_get_vaccine_dose(self):
        if hasattr(self, '_id') and not self.is_id_exist():
            raise exceptions.ValidationException({'id': messages.NOT_EXIST})

    def extra_validate_to_create_vaccine_dose(self):
        if hasattr(self, '_vaccine_id') and not self.is_vaccine_id_exist():
            raise exceptions.ValidationException({'vaccine_id': messages.NOT_EXIST})
        if hasattr(self, '_custom_user_code') and not self.is_custom_user_code_exist():
            raise exceptions.ValidationException({'custom_user_code': messages.NOT_EXIST})
        if self.is_vaccine_custom_user_injection_date_exist():
            raise exceptions.ValidationException({'vaccine_id,custom_user_code,injection_date': messages.EXIST})

    def extra_validate_to_update_vaccine_dose(self):
        if hasattr(self, '_id') and not self.is_id_exist():
            raise exceptions.ValidationException({'id': messages.NOT_EXIST})
        if hasattr(self, '_vaccine_id'):
            if not self._vaccine_id:
                raise exceptions.ValidationException({'vaccine_id': messages.EMPTY})
            elif not self.is_vaccine_id_exist():
                raise exceptions.ValidationException({'vaccine_id': messages.NOT_EXIST})

        new_vaccine_dose = self.get_vaccine_dose_by_vaccine_custom_user_injection_date(
            vaccine=self._vaccine if hasattr(self, '_vaccine') else self._vaccine_dose.vaccine,
            custom_user=self._vaccine_dose.custom_user,
            injection_date=self._injection_date if hasattr(self, '_injection_date') else self._vaccine_dose.injection_date,
        )
        if new_vaccine_dose and new_vaccine_dose != self._vaccine_dose:
            raise exceptions.ValidationException({'vaccine_id,custom_user_code,injection_date': messages.EXIST})

    def extra_validate_to_delete_vaccine_dose(self):
        if hasattr(self, '_id') and not self.is_id_exist():
            raise exceptions.ValidationException({'id': messages.NOT_EXIST})

    def extra_validate_to_filter_vaccine_dose(self):
        if hasattr(self, '_custom_user_code'):
            if self._custom_user_code:
                if not self.is_custom_user_code_exist():
                    raise exceptions.ValidationException({'custom_user_code': messages.NOT_EXIST})
            else:
                raise exceptions.ValidationException({'custom_user_code': messages.EMPTY})
