import jwt
from functools import wraps
from flask import request
from jwt import InvalidTokenError, PyJWTError

from core.config import settings
from .errors import ForbiddenError


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            raise ForbiddenError("Токен отсутствует или невалиден", status_code=401)

        token = auth_header.split(" ")[1]
        try:
            payload = jwt.decode(token, settings.DJANGO_SECRET_KEY, algorithms=["HS256"])
            kwargs['user_id'] = int(payload.get("user_id"))
        except jwt.ExpiredSignatureError:
            raise ForbiddenError("Срок действия токена истек", status_code=401)
        except InvalidTokenError:
            raise ForbiddenError("Невалидный токен", status_code=401)
        except PyJWTError:
            raise ForbiddenError("Ошибка авторизации", status_code=401)

        return f(*args, **kwargs)

    return decorated
