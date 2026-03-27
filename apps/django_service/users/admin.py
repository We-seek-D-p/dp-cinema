from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import ngettext

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        (
            "Кинотеатр: Доп. инфо",
            {"fields": ("avatar_url", "birth_date", "is_premium", "deleted_at")},
        ),
    )
    list_display = ("username", "email", "is_premium", "is_active", "date_joined")
    list_filter = ("is_premium", "is_staff", "is_active", "is_superuser")
    search_fields = ("username", "email", "first_name", "last_name")
    actions = ("grant_premium",)

    @admin.action(description="Выдать Premium")
    def grant_premium(self, request, queryset):
        updated = queryset.update(is_premium=True)
        self.message_user(
            request,
            ngettext(
                "%d пользователь получил статус Premium.",
                "%d пользователей получили статус Premium.",
                updated,
            )
            % updated,
            messages.SUCCESS,
        )
