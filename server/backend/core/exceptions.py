class ApplicationException(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class ValidationError(ApplicationException):
    pass


class NotFoundError(ApplicationException):
    pass


class AccessDeniedError(ApplicationException):
    pass


class ConflictError(ApplicationException):
    pass
