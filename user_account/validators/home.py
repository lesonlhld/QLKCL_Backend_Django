from django.db.models import Q
from address.models import City, District, Ward
from quarantine_ward.models import QuarantineWard
from utils import validators, messages, exceptions

class HomeValidator(validators.AbstractRequestValidate):

    def is_valid_fields(self, keys: list):
        ignorable_fields = {}
        set_of_keys = set(keys)

        return super().is_valid_fields(set_of_keys)

    def is_validate_number_of_days_in_out(self):
        if hasattr(self, '_number_of_days_in_out'):
            self._number_of_days_in_out = validators.PositiveIntegerValidator.valid(
                self._number_of_days_in_out,
                message={'number_of_days_in_out': messages.INVALID},
                message1={'number_of_days_in_out': messages.INVALID},
            )

    def is_city_id_exist(self, id):
        try:
            validators.ModelInstanceExistenceValidator.valid(
                model_cls=City,
                query_expr=Q(id=id),
            )
            return True
        except Exception as exception:
            return False

    def is_district_id_exist(self, id):
        try:
            validators.ModelInstanceExistenceValidator.valid(
                model_cls=District,
                query_expr=Q(id=id),
            )
            return True
        except Exception as exception:
            return False

    def is_ward_id_exist(self, id):
        try:
            validators.ModelInstanceExistenceValidator.valid(
                model_cls=Ward,
                query_expr=Q(id=id),
            )
            return True
        except Exception as exception:
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
        else:
            return False

    def is_validate_address_type(self):
        if hasattr(self, '_address_type'):
            if self._address_type not in ['city', 'district', 'ward']:
                raise exceptions.ValidationException({'address_type': messages.INVALID})

    def is_validate_start_time_max(self):
        if hasattr(self, '_start_time_max') and self._start_time_max != None:
            self._start_time_max = validators.DateTimeFieldValidator.valid(
                value=self._start_time_max,
                message={'start_time_max': messages.INVALID_DATETIME},
            )
    
    def is_validate_start_time_min(self):
        if hasattr(self, '_start_time_min') and self._start_time_min != None:
            self._start_time_min = validators.DateTimeFieldValidator.valid(
                value=self._start_time_min,
                message={'start_time_min': messages.INVALID_DATETIME},
            )

    def extra_validate_to_get_manager_home(self):
        if hasattr(self, '_quarantine_ward_id'):
            if not self.is_quarantine_ward_id_exist():
                raise exceptions.ValidationException({'quarantine_ward_id': messages.NOT_EXIST})

    def extra_validate_to_filter_address_with_num_of_members_pass_by(self):
        if self._address_type == 'city':
            # dont care about father_address_id
            ...
        elif self._address_type == 'district':
            if hasattr(self, '_father_address_id') and self._father_address_id:
                if not self.is_city_id_exist(self._father_address_id):
                    raise exceptions.ValidationException({'father_address_id': messages.NOT_EXIST})
            else:
                raise exceptions.ValidationException({'father_address_id': messages.EMPTY})
        else:
            if hasattr(self, '_father_address_id') and self._father_address_id:
                if not self.is_district_id_exist(self._father_address_id):
                    raise exceptions.ValidationException({'father_address_id': messages.NOT_EXIST})
            else:
                raise exceptions.ValidationException({'father_address_id': messages.EMPTY})
        if hasattr(self, '_quarantine_ward_id') and not self.is_quarantine_ward_id_exist():
            raise exceptions.ValidationException({'quarantine_ward_id': messages.NOT_EXIST})
        if hasattr(self, '_order_by'):
            if self._order_by not in ['name', '-name', 'num_of_members_pass_by', '-num_of_members_pass_by']:
                raise exceptions.ValidationException({'order_by': messages.INVALID})
        if hasattr(self, '_start_time_max') and not self._start_time_max:
            raise exceptions.ValidationException({'start_time_max': messages.EMPTY})
        if hasattr(self, '_start_time_min') and not self._start_time_min:
            raise exceptions.ValidationException({'start_time_min': messages.EMPTY})
        if hasattr(self, '_start_time_max') and self._start_time_max \
            and hasattr(self, '_start_time_min') and self._start_time_min:
            if self._start_time_min > self._start_time_max:
                raise exceptions.ValidationException({'start_time_max': messages.INVALID})