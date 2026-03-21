from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User
from .repositories import UserRepository


class UserService:
    def __init__(self):
        self.repo = UserRepository()

    def get_profile(self, user_id: int):
        return self.repo.get_by_id(user_id)

    def find_by_email(self, email: str):
        return self.repo.get_by_email(email)

    def register(self, data: dict):
        return self.repo.create(data)

    def authenticate_user(self, data: dict) -> dict | None:
        username = data.get('username')
        password = data.get('password')

        user = authenticate(username=username, password=password)

        if user and user.is_active:
            # 2. Если всё ок — генерим пару токенов (бизнес-задача сервиса)
            refresh = RefreshToken.for_user(user)
            return {
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': user
            }
        return None

    def update_profile(self, user_id: int, data: dict):
        user = self.repo.get_by_id(user_id)
        if user:
            return self.repo.update(user, data)
        return None

    def deactivate_account(self, user_id: int):
        user = self.repo.get_by_id(user_id)
        if user:
            self.repo.soft_delete(user)
            return True
        return False

    def recover_account(self, email: str) -> User | None:
        user = self.repo.get_any_by_email(email)
        if user and user.deleted_at:
            return self.repo.restore(user)
        return None
