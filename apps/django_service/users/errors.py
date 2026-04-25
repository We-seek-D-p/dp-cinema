from common.errors import DomainError
from rest_framework import status


class UserNotFoundError(DomainError):
    default_code = "user_not_found"
    default_message = "User does not exist"
    http_status_code = status.HTTP_404_NOT_FOUND


class UserAlreadyExistsError(DomainError):
    default_code = "user_already_exists"
    default_message = "User already exists"
    http_status_code = status.HTTP_409_CONFLICT


class InvalidCredentialsError(DomainError):
    default_code = "invalid_credentials"
    default_message = "Invalid credentials"
    http_status_code = status.HTTP_401_UNAUTHORIZED


class UserDeactivatedError(DomainError):
    default_code = "user_deactivated"
    default_message = "User account is deactivated"
    http_status_code = status.HTTP_403_FORBIDDEN


class PermissionDeniedError(DomainError):
    default_code = "permission_denied"
    default_message = "Permission denied"
    http_status_code = status.HTTP_403_FORBIDDEN


class UserRecoveryError(DomainError):
    default_code = "user_recovery"
    default_message = "User recovery failed"
    http_status_code = status.HTTP_404_NOT_FOUND


class EmailRequiredError(DomainError):
    default_code = "email_required"
    default_message = "Email is required"
    http_status_code = status.HTTP_400_BAD_REQUEST


class UsernameRequiredError(DomainError):
    default_code = "username_required"
    default_message = "Username is required"
    http_status_code = status.HTTP_400_BAD_REQUEST

class InvalidSubscriptionDurationError(DomainError):
    default_code = "invalid_subscription_duration"
    default_message = "Subscription duration must be positive"
    http_status_code = status.HTTP_400_BAD_REQUEST

