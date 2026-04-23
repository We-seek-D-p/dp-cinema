from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User
from .repositories import UserRepository
from .errors import (
    UserNotFoundError,
    UserAlreadyExistsError,
    InvalidCredentialsError,
    UserDeactivatedError,
    PermissionDeniedError,
    UserRecoveryError,
    EmailRequiredError,
    UsernameRequiredError,
)


class UserService:
    def __init__(self):
        self.repo = UserRepository()

    def get_profile(self, user_id: int) -> User:
        user = self.repo.get_any_by_id(user_id)
        if not user:
            raise UserNotFoundError()
        if user.deleted_at:
            raise UserDeactivatedError()
        return user

    def find_by_email(self, email: str):
        return self.repo.get_by_email(email)

    def register(self, data: dict) -> User:
        email = data.get("email")
        username = data.get("username")

        if not email:
            raise EmailRequiredError()
        if not username:
            raise UsernameRequiredError()

        if self.repo.get_by_email(email):
            raise UserAlreadyExistsError("User with this email already exists")
        if self.repo.get_by_username(username):
            raise UserAlreadyExistsError("User with this username already exists")

        return self.repo.create(data)

    def authenticate_user(self, data: dict) -> dict:
        username = data.get("username")
        password = data.get("password")

        user = authenticate(username=username, password=password)

        if not user:
            user_any = self.repo.get_any_by_username(username)
            if user_any and user_any.deleted_at:
                raise UserDeactivatedError()
            raise InvalidCredentialsError()
        if user.deleted_at or not user.is_active:
            raise UserDeactivatedError()

        ref = RefreshToken.for_user(user)
        return {
            "access": str(ref.access_token),
            "refresh": str(ref),
            "user": user,
        }

    def update_profile(self, user_id: int, data: dict, request_user: User) -> User:
        if request_user.id != user_id:
            raise PermissionDeniedError()

        user = self.get_profile(user_id)
        return self.repo.update(user, data)

    def deactivate_account(self, user_id: int, request_user: User) -> None:
        if request_user.id != user_id:
            raise PermissionDeniedError()

        user = self.get_profile(user_id)
        self.repo.soft_delete(user)

    def recover_account(self, email: str) -> User:
        if not email:
            raise EmailRequiredError()

        user = self.repo.get_any_by_email(email)
        if not user or not user.deleted_at:
            raise UserRecoveryError()
        return self.repo.restore(user)
