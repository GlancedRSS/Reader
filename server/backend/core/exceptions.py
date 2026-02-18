"""Common exception types for the application with HTTP status mapping."""


class ApplicationException(Exception):
    """Base exception for all application errors."""

    def __init__(self, message: str):
        """Initialize the exception with a message."""
        self.message = message
        super().__init__(message)


class ValidationError(ApplicationException):
    """Raised when input validation fails (HTTP 400)."""

    pass


class NotFoundError(ApplicationException):
    """Raised when a requested resource is not found (HTTP 404)."""

    pass


class AccessDeniedError(ApplicationException):
    """Raised when user lacks permission to access a resource (HTTP 403)."""

    pass


class ConflictError(ApplicationException):
    """Raised when a request conflicts with existing state (HTTP 409)."""

    pass
