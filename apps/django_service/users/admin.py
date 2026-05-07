from datetime import timedelta

from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin
from django.utils import timezone
from django.utils.translation import ngettext

from .models import Subscription, User


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("user", "subscribed_at", "expires_at", "is_active_display")
    list_filter = ("expires_at",)

    @admin.display(boolean=True, description="Активна")
    def is_active_display(self, obj):
        return obj.expires_at > timezone.now()


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        (
            "Кинотеатр: Доп. инфо",
            {"fields": ("avatar_url", "birth_date", "deleted_at")},
        ),
    )
    list_display = ("username", "email", "is_premium_display", "is_active", "date_joined")
    list_filter = ("is_staff", "is_active", "is_superuser")
    search_fields = ("username", "email", "first_name", "last_name")
    actions = ("grant_premium_month",)

    @admin.display(boolean=True, description="Premium")
    def is_premium_display(self, obj):
        return obj.is_premium

    @admin.action(description="Выдать Premium на 30 дней")
    def grant_premium_month(self, request, queryset):
        new_subs = [
            Subscription(user=user, expires_at=timezone.now() + timedelta(days=30))
            for user in queryset
        ]
        Subscription.objects.bulk_create(new_subs)

        count = len(new_subs)
        self.message_user(
            request,
            ngettext(
                "%d пользователь получил подписку.",
                "%d пользователей получили подписку.",
                count,
            )
            % count,
            messages.SUCCESS,
        )
