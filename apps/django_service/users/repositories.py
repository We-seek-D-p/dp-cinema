from django.utils import timezone

from .models import User


class UserRepository:
    def get_by_id(self, user_id: int):
        return User.objects.filter(id=user_id).first()

    def get_by_email(self, email: str):
        return User.objects.filter(email=email).first()

    def list_active(self):
        return User.objects.all()

    def create(self, data: dict):
        return User.objects.create_user(**data)

    def get_by_username(self, username: str) -> User:
        return User.objects.filter(username=username).first()

    def update(self, user: User, data: dict):
        for key, value in data.items():
            setattr(user, key, value)
        user.save()
        return user

    def soft_delete(self, user: User):
        user.deleted_at = timezone.now()
        user.is_active = False
        user.save()

    def get_any_by_email(self, email: str) -> User:
        return User.all_with_deleted.filter(email=email).first()

    def restore(self, user: User) -> User:
        user.deleted_at = None
        user.is_active = True
        user.save()
        return user
