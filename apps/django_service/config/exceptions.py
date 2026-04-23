from rest_framework.views import exception_handler
from rest_framework.response import Response

from apps.django_service.common.errors import DomainError


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is None and isinstance(exc, DomainError):
        return exc.to_response()

    return response