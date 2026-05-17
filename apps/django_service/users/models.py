from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.db.models import Exists, OuterRef
from django.utils import timezone


class Subscription(models.Model):
    user = models.ForeignKey(
        "User",
        on_delete=models.CASCADE,
        related_name="subscriptions",
    )
    subscribed_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    class Meta:
        db_table = "subscriptions"
        indexes = [models.Index(fields=["user", "expires_at"])]

    @classmethod
    def check_expiration(cls):
        return models.Q(expires_at__gt=timezone.now())


class ActiveUserManager(UserManager):
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(deleted_at__isnull=True)
            .annotate(
                _is_premium=Exists(
                    Subscription.objects.filter(
                        Subscription.check_expiration(), user=OuterRef("pk")
                    )
                )
            )
        )


class User(AbstractUser):
    email = models.EmailField(unique=True)
    avatar_url = models.URLField(max_length=500, null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True)

    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = ActiveUserManager()
    all_with_deleted = models.Manager()

    class Meta:
        db_table = "users"

    @property
    def is_premium(self):
        if hasattr(self, "_is_premium"):
            return self._is_premium
        return self.subscriptions.filter(Subscription.check_expiration()).exists()
