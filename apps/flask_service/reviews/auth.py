import hmac
from functools import wraps

import jwt
from core.config import settings
from flask import request
from jwt import InvalidTokenError, PyJWTError

from .errors import ForbiddenError


def _extract_token_from_header(auth_header: str | None) -> str:
    if not auth_header:
        raise ForbiddenError("Отсутствует заголовок Authorization", status_code=401)

    parts = auth_header.split()
    if len(parts) != 2:
        raise ForbiddenError(
            "Неверный формат Authorization. Ожидается: Bearer <token>",
            status_code=401,
        )

    scheme, token = parts
    if scheme.lower() != "bearer":
        raise ForbiddenError(
            "Неверная схема авторизации. Ожидается: Bearer",
            status_code=401,
        )

    if not token or not token.strip():
        raise ForbiddenError("Токен не может быть пустым", status_code=401)

    return token


def _decode_and_validate_jwt(token: str) -> int:
    try:
        payload = jwt.decode(token, settings.DJANGO_SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("user_id")
        if user_id is None:
            raise ForbiddenError("Токен не содержит user_id", status_code=401)
        return int(user_id)
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


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        token = _extract_token_from_header(auth_header)
        user_id = _decode_and_validate_jwt(token)
        kwargs["user_id"] = user_id
        return f(*args, **kwargs)

    return decorated


def internal_token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        internal_token = request.headers.get("X-Internal-Token")
        expected_token = settings.INTERNAL_SERVICE_TOKEN

        if not internal_token:
            raise ForbiddenError("Отсутствует X-Internal-Token", status_code=403)

        if not hmac.compare_digest(internal_token, expected_token):
            raise ForbiddenError("Неверный X-Internal-Token", status_code=403)

        return f(*args, **kwargs)

    return decorated
