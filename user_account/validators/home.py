from utils import validators, messages

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
