from django.db.models import Q
from ..models import CustomUser, DestinationHistory
from address.models import Country, City, District, Ward
from utils import validators, messages, exceptions

class DestinationHistoryValidator(validators.AbstractRequestValidate):

    def is_valid_fields(self, keys: list):
        ignorable_fields = {}
        set_of_keys = set(keys)

        return super().is_valid_fields(set_of_keys)

    def is_validate_start_time(self):
        if hasattr(self, '_start_time') and self._start_time != None:
            self._start_time = validators.DateTimeFieldValidator.valid(
                value=self._start_time,
                message={'start_time': messages.INVALID_DATETIME},
            )
    
    def is_validate_end_time(self):
        if hasattr(self, '_end_time') and self._end_time != None:
            self._end_time = validators.DateTimeFieldValidator.valid(
                value=self._end_time,
                message={'end_time': messages.INVALID_DATETIME},
            )
    
    def is_id_exist(self):
        if hasattr(self, '_id'):
            try:
                self._destination_history = validators.ModelInstanceExistenceValidator.valid(
                    model_cls=DestinationHistory,
                    query_expr=Q(id=self._id),
                )
                return True
            except Exception as exception:
                return False
        return False

    def is_user_code_exist(self):
        if hasattr(self, '_user_code'):
            try:
                self._user = validators.ModelInstanceExistenceValidator.valid(
                    model_cls=CustomUser,
                    query_expr=Q(code=self._user_code),
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
        if hasattr(self, '_ward') and self._ward:
            if not hasattr(self, '_district'):
                self._district = self._ward.district
                self._district_id = self._ward.district.id
            else:
                if self._district != self._ward.district:
                    raise exceptions.ValidationException({'country_ward_relationship': messages.INVALID})
        
        if hasattr(self, '_district') and self._district:
            if not hasattr(self, '_city'):
                self._city = self._district.city
                self._city_id = self._district.city.id
            else:
                if self._city != self._district.city:
                    raise exceptions.ValidationException({'country_ward_relationship': messages.INVALID})

        if hasattr(self, '_city') and self._city:
            if not hasattr(self, '_country'):
                self._country = self._city.country
                self._country_code = self._city.country.code
            else:
                if self._country != self._city.country:
                    raise exceptions.ValidationException({'country_ward_relationship': messages.INVALID})

    def extra_validate_to_create_destination_history(self):
        if hasattr(self, '_user_code') and not self.is_user_code_exist():
            raise exceptions.NotFoundException({'user_code': messages.NOT_EXIST})
        if hasattr(self, '_country_code') and not self.is_country_code_exist():
            raise exceptions.NotFoundException({'country_code': messages.NOT_EXIST})
        if hasattr(self, '_city_id') and not self.is_city_id_exist():
            raise exceptions.NotFoundException({'city_id': messages.NOT_EXIST})
        if hasattr(self, '_district_id'):
            if self._district_id and not self.is_district_id_exist():
                raise exceptions.NotFoundException({'district_id': messages.NOT_EXIST})
        if hasattr(self, '_ward_id'):
            if self._ward_id and not self.is_ward_id_exist():
                raise exceptions.NotFoundException({'ward_id': messages.NOT_EXIST})
        self.check_country_ward_relationship()
        if hasattr(self, '_start_time') and self._start_time \
            and hasattr(self, '_end_time') and self._end_time:
            if self._start_time > self._end_time:
                raise exceptions.NotFoundException({'end_time': messages.INVALID})

    def extra_validate_to_get_destination_history(self):
        if hasattr(self, '_id') and not self.is_id_exist():
            raise exceptions.NotFoundException({'id': messages.NOT_EXIST})

    def extra_validate_to_update_destination_history(self):
        if hasattr(self, '_id') and not self.is_id_exist():
            raise exceptions.NotFoundException({'id': messages.NOT_EXIST})
        if hasattr(self, '_country_code'):
            if not self._country_code:
                raise exceptions.NotFoundException({'country_code': messages.EMPTY})
            elif not self.is_country_code_exist():
                raise exceptions.NotFoundException({'country_code': messages.NOT_EXIST})
        if hasattr(self, '_city_id'):
            if not self._city_id:
                raise exceptions.NotFoundException({'city_id': messages.EMPTY})
            elif not self.is_city_id_exist():
                raise exceptions.NotFoundException({'city_id': messages.NOT_EXIST})
        if hasattr(self, '_district_id'):
            if self._district_id:
                if not self.is_district_id_exist():
                    raise exceptions.NotFoundException({'district_id': messages.NOT_EXIST})
            else:
                self._district = None
        if hasattr(self, '_ward_id'):
            if self._ward_id:
                if not self.is_ward_id_exist():
                    raise exceptions.NotFoundException({'ward_id': messages.NOT_EXIST})
            else:
                self._ward = None
        self.check_country_ward_relationship()
        if hasattr(self, '_start_time'):
            if not self._start_time:
                raise exceptions.ValidationException({'start_time': messages.EMPTY})
        else:
            self._start_time = self._destination_history.start_time
        if not hasattr(self, '_end_time'):
            self._end_time = self._destination_history.end_time
        if self._start_time and self._end_time:
            if self._start_time > self._end_time:
                raise exceptions.NotFoundException({'end_time': messages.INVALID})

    def extra_validate_to_delete_destination_history(self):
        if hasattr(self, '_id') and not self.is_id_exist():
            raise exceptions.NotFoundException({'id': messages.NOT_EXIST})

    def extra_validate_to_filter_destination_history(self):
        if hasattr(self, '_user_code') and not self.is_user_code_exist():
            raise exceptions.NotFoundException({'user_code': messages.NOT_EXIST})