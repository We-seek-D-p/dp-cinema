from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

from apps.django_service.common.errors import DomainError
from apps.django_service.users.errors import (
    UserNotFoundError,
    UserAlreadyExistsError,
    InvalidCredentialsError,
    UserDeactivatedError,
    PermissionDeniedError,
    UserRecoveryError,
)
from apps.django_service.movies.errors import (
    MovieNotFoundError,
    AlreadyInWatchlistError,
    WatchlistItemNotFoundError,
    PremiumContentRestrictedError,
)


def _get_http_status_for_domain_error(exc: DomainError) -> int:
    """map: domain error to http status code"""
    mapping = {
        # Users
        UserNotFoundError: status.HTTP_404_NOT_FOUND,
        UserAlreadyExistsError: status.HTTP_409_CONFLICT,
        InvalidCredentialsError: status.HTTP_401_UNAUTHORIZED,
        UserDeactivatedError: status.HTTP_403_FORBIDDEN,
        PermissionDeniedError: status.HTTP_403_FORBIDDEN,
        UserRecoveryError: status.HTTP_404_NOT_FOUND,

        # Movies
        MovieNotFoundError: status.HTTP_404_NOT_FOUND,
        AlreadyInWatchlistError: status.HTTP_400_BAD_REQUEST,
        WatchlistItemNotFoundError: status.HTTP_404_NOT_FOUND,
        PremiumContentRestrictedError: status.HTTP_403_FORBIDDEN,
    }

    return mapping.get(exc.__class__, status.HTTP_400_BAD_REQUEST)


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is None and isinstance(exc, DomainError):
        http_status = _get_http_status_for_domain_error(exc)

        return Response(
            {"error": {"code": exc.code, "message": exc.message}},
            status=http_status,
        )

    return response