from django.contrib import admin, messages
from django.utils.translation import ngettext

from .models import Genre, Movie, Watchlist


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "created_at", "updated_at")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ("title", "is_published", "is_premium", "release_date", "deleted_at")
    list_filter = ("is_published", "is_premium", "genres", "deleted_at")
    list_editable = ("is_published",)
    search_fields = ("title", "description")
    autocomplete_fields = ("genres",)
    ordering = ("title",)
    actions = ("publish_movies",)

    @admin.action(description="Опубликовать")
    def publish_movies(self, request, queryset):
        updated = queryset.update(is_published=True)
        self.message_user(
            request,
            ngettext(
                "%d фильм опубликован.",
                "%d фильмов опубликовано.",
                updated,
            )
            % updated,
            messages.SUCCESS,
        )


@admin.register(Watchlist)
class WatchlistAdmin(admin.ModelAdmin):
    list_display = ("user", "movie", "added_at", "deleted_at")
    list_filter = ("added_at", "user", "deleted_at")
    search_fields = ("user__username", "movie__title")
