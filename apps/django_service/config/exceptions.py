from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from apps.django_service.common.errors import DomainError


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is None and isinstance(exc, DomainError):
        if exc.code == "MovieNotFoundError":
            http_status = status.HTTP_404_NOT_FOUND
        elif exc.code == "AlreadyInWatchlistError":
            http_status = status.HTTP_400_BAD_REQUEST
        elif exc.code == "PremiumContentRestrictedError":
            http_status = status.HTTP_403_FORBIDDEN
        else:
            http_status = status.HTTP_400_BAD_REQUEST

        return Response(
            {"error": {"code": exc.code, "message": exc.message}},
            status=http_status
        )

    return response
