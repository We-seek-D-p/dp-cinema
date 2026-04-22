from apps.django_service.common.errors import DomainError


class UserNotFoundError(DomainError):
    def __init__(self, message='User not found'):
        super().__init__(message)

class UserAlreadyExistsError(DomainError):
    def __init__(self, message='User with this email or username already exists'):
        super().__init__(message)

class InvalidCredentialsError(DomainError):
    def __init__(self, message='Invalid username or password'):
        super().__init__(message)

class UserDeactivatedError(DomainError):
    def __init__(self, message='User account is deactivated'):
        super().__init__(message)

class PermissionDeniedError(DomainError):
    def __init__(self, message='You don`t have permission to perform this action'):
        super().__init__(message)

class UserRecoveryError(DomainError):
    def __init__(self, message='Cannot recover account: user not found or already active'):
        super().__init__(message)