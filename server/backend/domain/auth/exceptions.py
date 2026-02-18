"""Domain exceptions for authentication and authorization errors."""


class AuthenticationError(Exception):
    """Base exception for authentication errors."""

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class InvalidCredentialsError(AuthenticationError):
    """Exception raised when credentials are invalid."""

    def __init__(self, message: str = "Invalid username or password"):
        super().__init__(message)


class InvalidPasswordError(AuthenticationError):
    """Exception raised when current password is invalid."""

    def __init__(self, message: str = "Invalid current password"):
        super().__init__(message)
