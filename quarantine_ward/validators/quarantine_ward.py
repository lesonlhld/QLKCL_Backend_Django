from ..models import QuarantineWard, Country, City, District, Ward
from utils import validators, exceptions, messages
from django.db.models import Q

class QuarantineWardValidator(validators.AbstractRequestValidate):

    def is_valid_fields(self, keys: list):
        ignorable_fields = {}
        set_of_keys = set(keys)

        return super().is_valid_fields(set_of_keys)
    
    def is_validate_email(self):
        value = self._email
        if value != None:
            self._email = validators.EmailValidator.valid(value)
        return self._email

    def is_validate_country(self):
        self._country = validators.ModelInstanceExistenceValidator.valid(
            model_cls=Country,
            query_expr=Q(
                code=self._country_code,
            ),
            message=messages.COUNTRY_NOT_FOUND,
        )
    
    def is_validate_city(self):
        self._city = validators.ModelInstanceExistenceValidator.valid(
            model_cls=City,
            query_expr=Q(
                code=self._city_code,
            ),
            message=messages.CITY_NOT_FOUND,
        )

    def is_validate_district(self):
        self._district = validators.ModelInstanceExistenceValidator.valid(
            model_cls=District,
            query_expr=Q(
                code=self._district_code,
            ),
            message=messages.DISTRICT_NOT_FOUND,
        )
    
    def is_validate_ward(self):
        self._ward = validators.ModelInstanceExistenceValidator.valid(
            model_cls=Ward,
            query_expr=Q(
                code=self._ward_code,
            ),
            message=messages.WARD_NOT_FOUND,
        )

