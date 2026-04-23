class DomainError(Exception):
    default_code = "domain_error"
    default_message = "Domain Error"
    http_status_code = 400

    def __init__(self, message=None, code=None, **kwargs):
        self.message = message or self.default_message
        self.code = code or self.default_code
        super().__init__(self.message)