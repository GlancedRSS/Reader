class AuthenticationError(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class InvalidCredentialsError(AuthenticationError):
    def __init__(self, message: str = "Invalid username or password"):
        super().__init__(message)


class InvalidPasswordError(AuthenticationError):
    def __init__(self, message: str = "Invalid current password"):
        super().__init__(message)
