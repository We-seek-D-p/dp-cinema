class ReviewError(Exception):
    message = "Internal server error"
    status_code = 500

    def __init__(self, message=None, status_code=None):
        if message:
            self.message = message
        if status_code:
            self.status_code = status_code
        super().__init__(self.message)


class ValidationError(ReviewError):
    message = "Некорректные данные ввода"
    status_code = 400


class ForbiddenError(ReviewError):
    message = "У вас нет прав для выполнения этого действия"
    status_code = 403


class ConflictError(ReviewError):
    message = "Рецензия уже существует"
    status_code = 409


class NotFoundError(ReviewError):
    message = "Объект не найден"
    status_code = 404


class DependencyError(ReviewError):
    message = "Ошибка внешней интеграции (Django)"
    status_code = 424
