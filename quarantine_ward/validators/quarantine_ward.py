from ..models import QuarantineWard, Country, City, District, Ward, CustomUser
from utils import validators, messages, enums, exceptions
from django.db.models import Q

class QuarantineWardValidator(validators.AbstractRequestValidate):

    def is_valid_fields(self, keys: list):
        ignorable_fields = {'country', 'city', 'district', 'address'}
        set_of_keys = set(keys) - ignorable_fields

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
                code=self._country,
            ),
            message=messages.COUNTRY_NOT_FOUND,
        )
        return self._country
    
    def is_validate_full_name(self):
        if self.is_full_name_exist():
            raise exceptions.InvalidArgumentException({'full_name': messages.EXIST})

    def is_full_name_exist(self):
        try:
            full_name = validators.ModelInstanceExistenceValidator.valid(
                model_cls=QuarantineWard,
                query_expr=Q(full_name=self._full_name),
                message={'full_name': messages.EXIST},
            )
            return True
        except Exception as exception:
            return False
    
    def is_validate_city(self):
        country = self.is_validate_country()
        self._city = validators.ModelInstanceExistenceValidator.valid(
            model_cls=City,
            query_expr=Q(
                id=self._city,
                country=country,
            ),
            message=messages.CITY_NOT_FOUND,
        )
        return self._city

    def is_validate_district(self):
        city = self.is_validate_city()
        self._district = validators.ModelInstanceExistenceValidator.valid(
            model_cls=District,
            query_expr=Q(
                id=self._district,
                city=city,
            ),
            message=messages.DISTRICT_NOT_FOUND,
        )
        return self._district
    
    def is_validate_ward(self):
        district = self.is_validate_district()
        self._ward = validators.ModelInstanceExistenceValidator.valid(
            model_cls=Ward,
            query_expr=Q(
                id=self._ward,
                district=district,
            ),
            message=messages.WARD_NOT_FOUND,
        )
        return self._ward

    def is_validate_latitude(self):
        self._latitude = validators.PositiveFloatValidator.valid(
            self._latitude,
        )

    def is_validate_longitude(self):
        self._longitude = validators.PositiveFloatValidator.valid(
            self._longitude,
        )
    
    def is_validate_status(self):
        value = self._status
        if value != None:
            self._status = validators.EnumValidator.valid(
                value, 
                enums.QuarantineWardStatus, 
                messages.INVALID_STATUS,
            )
    
    def is_validate_type(self):
        value = self._type
        if value != None:
            self._type = validators.EnumValidator.valid(
                value, 
                enums.QuarantineWardType, 
                messages.INVALID_TYPE,
            )

    def is_validate_quarantine_time(self):
        value = self._quarantine_time
        if value != None:
            self._quarantine_time = validators.PositiveFloatValidator.valid(
                value, 
                messages.INVALID_QUARANTINE_TIME,
            )
    
    def is_validate_main_manager(self):
        self._main_manager = validators.ModelInstanceExistenceValidator.valid(
            model_cls=CustomUser,
            query_expr=Q(
                id=self._main_manager,
            ),
            message=messages.USER_NOT_FOUND,
        )
    
    def is_validate_id(self):
        self._id = validators.ModelInstanceExistenceValidator.valid(
            model_cls=QuarantineWard,
            query_expr=Q(
                id=self._id,
            ),
            message=messages.QUARANTINE_WARD_NOT_FOUND,
        )
