from django.db.models import Q
from ..models import Vaccine
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
