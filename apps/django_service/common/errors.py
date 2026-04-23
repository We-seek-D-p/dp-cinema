from rest_framework.response import Response


class DomainError(Exception):
    default_code = "domain_error"
    default_message = "Domain Error"
    http_status_code = 400

    def __init__(self, message=None, code=None, http_status_code=None, **kwargs):
        self.message = message or self.default_message
        self.code = code or self.default_code
        self.http_status_code = code or self.http_status_code
        self.kwargs = kwargs
        super().__init__(self.message)

    def to_response(self):
        data = {'error': {'code': self.code, 'message': self.message}}
        if self.kwargs:
            data['error']['details'] = self.kwargs
        return Response(data, status=self.http_status_code)