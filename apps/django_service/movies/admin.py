from django.contrib import admin, messages
from django.utils.translation import ngettext

from .models import Genre, Movie, Watchlist
from .services import MovieUploadService


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "created_at", "updated_at")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "is_published",
        "is_premium",
        "release_date",
        "processing_status",
        "processing_task_id",
        "deleted_at",
    )
    list_filter = (
        "is_published",
        "is_premium",
        "genres",
        "processing_status",
        "deleted_at",
    )
    list_editable = ("is_published",)
    search_fields = ("title", "description")
    autocomplete_fields = ("genres",)
    ordering = ("title",)
    actions = ("publish_movies", "start_processing")
    readonly_fields = (
        "processing_status",
        "processing_task_id",
        "processing_error",
    )
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "title",
                    "description",
                    "source_url",
                    "poster_url",
                    "hls_url",
                    "release_date",
                    "genres",
                    "is_premium",
                    "is_published",
                )
            },
        ),
        (
            "Processing",
            {
                "fields": (
                    "processing_status",
                    "processing_task_id",
                    "processing_error",
                )
            },
        ),
    )

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

    @admin.action(description="Запустить обработку видео")
    def start_processing(self, request, queryset):
        service = MovieUploadService()

        accepted = 0
        skipped_missing_source = 0
        failed = 0

        for movie in queryset:
            if not movie.source_url:
                skipped_missing_source += 1
                continue

            try:
                result = service.process_movie(movie.id, None)
                if "error" in result:
                    failed += 1
                else:
                    accepted += 1
            except Exception:
                failed += 1

        if accepted:
            self.message_user(
                request,
                ngettext(
                    "%d фильм отправлен в обработку.",
                    "%d фильмов отправлено в обработку.",
                    accepted,
                )
                % accepted,
                messages.SUCCESS,
            )

        if skipped_missing_source:
            self.message_user(
                request,
                ngettext(
                    "%d фильм пропущен: не указан source_url.",
                    "%d фильмов пропущено: не указан source_url.",
                    skipped_missing_source,
                )
                % skipped_missing_source,
                messages.WARNING,
            )

        if failed:
            self.message_user(
                request,
                ngettext(
                    "%d фильм не удалось отправить в обработку.",
                    "%d фильмов не удалось отправить в обработку.",
                    failed,
                )
                % failed,
                messages.ERROR,
            )


@admin.register(Watchlist)
class WatchlistAdmin(admin.ModelAdmin):
    list_display = ("user", "movie", "added_at", "deleted_at")
    list_filter = ("added_at", "user", "deleted_at")
    search_fields = ("user__username", "movie__title")
