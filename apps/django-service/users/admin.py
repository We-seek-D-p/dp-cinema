from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Кинотеатр: Доп. инфо', {'fields': ('avatar_url', 'birth_date', 'is_premium', 'deleted_at')}),
    )
    list_display = ('username', 'email', 'is_premium', 'is_active', 'date_joined')
