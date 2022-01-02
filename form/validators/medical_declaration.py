from django.db.models import Q
from ..models import MedicalDeclaration
from user_account.models import CustomUser
from form.models import Symptom
from utils import validators, messages, exceptions
from utils.enums import SymptomType, HealthDeclarationConclude
from utils.tools import split_input_list, date_string_to_timestamp

class MedicalDeclarationValidator(validators.AbstractRequestValidate):

    def is_valid_fields(self, keys: list):
        ignorable_fields = {}
        set_of_keys = set(keys)

        return super().is_valid_fields(set_of_keys)

    def is_validate_phone_number(self):
        if hasattr(self, '_phone_number'):
            self._phone_number = validators.PhoneNumberValidator.valid(self._phone_number)

    def is_validate_heartbeat(self):
        if hasattr(self, '_heartbeat'):
            self._heartbeat = validators.PositiveIntegerValidator.valid(
                self._heartbeat,
                message={'heartbeat': messages.INVALID_POSITIVE_INTEGER},
                message1={'heartbeat': messages.CANNOT_CONVERT_STRING_TO_INT},
            )

    def is_validate_temperature(self):
        if hasattr(self, '_temperature'):
            self._temperature = validators.PositiveFloatValidator.valid(
                self._temperature,
                message={'temperature': messages.INVALID_POSITIVE_FLOAT},
                message1={'temperature': messages.CANNOT_CONVERT_STRING_TO_FLOAT},
            )

    def is_validate_breathing(self):
        if hasattr(self, '_breathing'):
            self._breathing = validators.PositiveIntegerValidator.valid(
                self._breathing,
                message={'breathing': messages.INVALID_POSITIVE_INTEGER},
                message1={'breathing': messages.CANNOT_CONVERT_STRING_TO_INT},
            )

    def is_validate_spo2(self):
        if hasattr(self, '_spo2'):
            self._spo2 = validators.PositiveFloatValidator.valid(
                self._spo2,
                message={'spo2': messages.INVALID_POSITIVE_FLOAT},
                message1={'spo2': messages.CANNOT_CONVERT_STRING_TO_FLOAT},
            )

    def is_validate_blood_pressure(self):
        if hasattr(self, '_blood_pressure'):
            self._blood_pressure = validators.PositiveFloatValidator.valid(
                self._blood_pressure,
                message={'blood_pressure': messages.INVALID_POSITIVE_FLOAT},
                message1={'blood_pressure': messages.CANNOT_CONVERT_STRING_TO_FLOAT},
            )

    def is_validate_main_symptoms(self):
        if hasattr(self, '_main_symptoms') and self._main_symptoms != None:
            self._list_main_symptoms_objects = []
            self._list_main_symptoms_ids = split_input_list(self._main_symptoms)
            for item in self._list_main_symptoms_ids:
                try:
                    object = validators.ModelInstanceExistenceValidator.valid(
                        model_cls=Symptom,
                        query_expr=Q(id=item, type=SymptomType.MAIN),
                    )
                    self._list_main_symptoms_objects += [object]
                except Exception as exception:
                    raise exceptions.NotFoundException({'main_symptoms': messages.NOT_EXIST})

    def is_validate_extra_symptoms(self):
        if hasattr(self, '_extra_symptoms') and self._extra_symptoms != None:
            self._list_extra_symptoms_objects = []
            self._list_extra_symptoms_ids = split_input_list(self._extra_symptoms)
            for item in self._list_extra_symptoms_ids:
                try:
                    object = validators.ModelInstanceExistenceValidator.valid(
                        model_cls=Symptom,
                        query_expr=Q(id=item, type=SymptomType.EXTRA),
                    )
                    self._list_extra_symptoms_objects += [object]
                except Exception as exception:
                    raise exceptions.NotFoundException({'extra_symptoms': messages.NOT_EXIST})

    def is_id_exist(self):
        if hasattr(self, '_id'):
            try:
                self._medical_declaration = validators.ModelInstanceExistenceValidator.valid(
                    model_cls=MedicalDeclaration,
                    query_expr=Q(id=self._id),
                )
                return True
            except Exception as exception:
                return False
        return False

    def is_code_exist(self, code=None):
        if code:
            try:
                validators.ModelInstanceExistenceValidator.valid(
                    model_cls=MedicalDeclaration,
                    query_expr=Q(code=code),
                )
                return True
            except Exception as exception:
                return False
        else:
            if hasattr(self, '_code'):
                try:
                    self._medical_declaration = validators.ModelInstanceExistenceValidator.valid(
                        model_cls=MedicalDeclaration,
                        query_expr=Q(code=self._code),
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

    def is_phone_number_exist(self):
        if hasattr(self, '_phone_number'):
            try:
                self._user = validators.ModelInstanceExistenceValidator.valid(
                    model_cls=CustomUser,
                    query_expr=Q(phone_number=self._phone_number),
                )
                return True
            except Exception as exception:
                return False
        return False

    def set_conclude_when_create_medical_declaration(self):
        self._conclude = HealthDeclarationConclude.NORMAL

        if hasattr(self, '_list_extra_symptoms_objects'):
            if len(self._list_extra_symptoms_objects) > 0:
                self._conclude = HealthDeclarationConclude.UNWELL

        if hasattr(self, '_list_main_symptoms_objects'):
            if len(self._list_main_symptoms_objects) > 0:
                self._conclude = HealthDeclarationConclude.SERIOUS

    def extra_validate_to_create_medical_declaration(self):
        if hasattr(self, '_phone_number') and not self.is_phone_number_exist():
            raise exceptions.ValidationException({'phone_number': messages.NOT_EXIST})
        self.set_conclude_when_create_medical_declaration()
        
        
    def extra_validate_to_get_medical_declaration(self):
        if hasattr(self, '_id') and not self.is_id_exist():
            raise exceptions.ValidationException({'id': messages.NOT_EXIST})

    def extra_validate_to_filter_medical_declaration(self):
        if hasattr(self, '_user_code') and not self.is_user_code_exist():
            raise exceptions.ValidationException({'main': messages.USER_NOT_FOUND})
        if hasattr(self, '_created_at_max'):
            validators.DateStringValidator.valid(self._created_at_max, message={'created_at_max': messages.INVALID})
            self._created_at_max = date_string_to_timestamp(self._created_at_max, 1)
        if hasattr(self, '_created_at_min'):
            validators.DateStringValidator.valid(self._created_at_min, message={'created_at_min': messages.INVALID})
            self._created_at_min = date_string_to_timestamp(self._created_at_min, 0)
