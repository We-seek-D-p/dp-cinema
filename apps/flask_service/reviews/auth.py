from functools import wraps

import jwt
from core.config import settings
from flask import request
from jwt import InvalidTokenError, PyJWTError

from .errors import ForbiddenError


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise ForbiddenError("Токен отсутствует или невалиден", status_code=401)

        token = auth_header.split(" ")[1]
        if not token:
            raise ForbiddenError("Токен отсутствует", status_code=401)

        try:
            payload = jwt.decode(
                token, settings.DJANGO_SECRET_KEY, algorithms=["HS256"]
            )
            user_id = payload.get("user_id")
            if user_id is None:
                raise ForbiddenError("Токен не содержит user_id", status_code=401)
            kwargs["user_id"] = int(user_id)
        except jwt.ExpiredSignatureError as err:
            raise ForbiddenError("Срок действия токена истек", status_code=401) from err
        except InvalidTokenError as err:
            raise ForbiddenError("Невалидный токен", status_code=401) from err
        except PyJWTError as err:
            raise ForbiddenError("Ошибка авторизации", status_code=401) from err
        except (TypeError, ValueError) as err:
            raise ForbiddenError(
                "Неверный формат user_id в токене", status_code=401
            ) from err

        return f(*args, **kwargs)

    return decorated
