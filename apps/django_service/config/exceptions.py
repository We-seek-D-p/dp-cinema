from common.errors import DomainError
from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is None and isinstance(exc, DomainError):
        return exc.to_response()

    return response
