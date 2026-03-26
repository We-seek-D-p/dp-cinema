from django.contrib import admin

from .models import Genre, Movie, Watchlist


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "created_at", "updated_at")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ("title", "is_published", "is_premium", "release_date")
    list_filter = ("is_published", "is_premium", "genres")
    list_editable = ("is_published",)
    search_fields = ("title", "description")
    autocomplete_fields = ("genres",)
    ordering = ("title",)


@admin.register(Watchlist)
class WatchlistAdmin(admin.ModelAdmin):
    list_display = ("user", "movie", "added_at")
    list_filter = ("added_at", "user")
    search_fields = ("user__username", "movie__title")
