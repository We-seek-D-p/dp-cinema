from rest_framework.response import Response
from rest_framework import status


class DomainError(Exception):
    default_code = "domain_error"
    default_message = "Domain Error"
    http_status_code = status.HTTP_400_BAD_REQUEST

    def __init__(self, message=None, code=None, http_status_code=None):
        self.message = message or self.default_message
        self.code = code or self.default_code
        self.http_status_code = http_status_code or self.http_status_code
        super().__init__(self.message)

    def to_response(self):
        data = {'error': {'code': self.code, 'message': self.message}}
        return Response(data, status=self.http_status_code)