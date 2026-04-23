from apps.django_service.common.errors import DomainError


class UserNotFoundError(DomainError):
    default_code = 'user_not_found'
    default_message = 'User does not exist'
    http_status_code = 404

class UserAlreadyExistsError(DomainError):
    default_code = 'user_already_exists'
    default_message = 'User already exists'
    http_status_code = 409

class InvalidCredentialsError(DomainError):
    default_code = 'invalid_credentials'
    default_message = 'Invalid credentials'
    http_status_code = 401

class UserDeactivatedError(DomainError):
    default_code = 'user_deactivated'
    default_message = 'User account is deactivated'
    http_status_code = 403

class PermissionDeniedError(DomainError):
    default_code = 'permission_denied'
    default_message = ('Permission denied')
    http_status_code = 403

class UserRecoveryError(DomainError):
    default_code = 'user_recovery'
    default_message = 'User recovery failed'
    http_status_code = 404