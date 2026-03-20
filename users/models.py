from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models


class ActiveUserManager(UserManager):
    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)


class User(AbstractUser):
    email = models.EmailField(unique=True)
    avatar_url = models.URLField(max_length=500, null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True)

    is_premium = models.BooleanField(default=False)

    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = ActiveUserManager()
    all_with_deleted = models.Manager()

    class Meta:
        db_table = 'users'
