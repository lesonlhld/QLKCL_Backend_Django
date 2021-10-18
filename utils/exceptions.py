from . import messages

class ApplicationException(Exception):
    def __init__(self, message = messages.CONTACT_ADMIN_FOR_SUPPORT):
        self.message = message
        super().__init__(self.message)
        
class AuthenticationException(ApplicationException):
    def __init__(self, message = messages.NO_PERMISSION):
        self.message = message
        super().__init__(self.message)

class InvalidArgumentException(ApplicationException):
    def __init__(self, message = messages.INVALID_ARGUMENT):
        self.message = message
        super().__init__(self.message)

class NotFoundException(ApplicationException):
    def __init__(self, message = messages.NOT_FOUND_EXCEPTION):
        self.message = message
        super().__init__(self.message)

class NetworkException(ApplicationException):
    def __init__(self, message = messages.NETWORK_EXCEPTION):
        self.message = message
        super().__init__(self.message)

class ValidationException(ApplicationException):
    def __init__(self, message = messages.VALIDATION_EXCEPTION):
        self.message = message
        super().__init__(self.message)
