from django.contrib import admin, messages
from django.utils.translation import ngettext
from reviews.models import Review, ReviewStatus
from reviews.services import FlaskReviewsClient


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "movie",
        "user_id",
        "rating",
        "status",
        "text",
        "created_at",
    )
    list_filter = ("status", "rating", "created_at")
    list_editable = ("status",)
    search_fields = ("text", "movie__title")
    actions = ("approve_reviews", "hide_reviews")
    readonly_fields = ("id", "user_id", "created_at", "updated_at", "text")

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ("id", "user_id", "created_at", "updated_at")
        return ("created_at", "updated_at")

    def save_model(self, request, obj, form, change) -> None:
        if change:
            if "status" in form.changed_data:
                success = FlaskReviewsClient.send_status_update(obj.id, obj.status)
                if not success:
                    self.message_user(
                        request,
                        f"Статус отзыва {obj.id} изменен в Django, но не синхронизирован с Flask.",
                        messages.WARNING,
                    )
        super().save_model(request, obj, form, change)

    def approve_reviews(self, request, queryset):
        success_count = 0
        for review in queryset:
            if FlaskReviewsClient.send_status_update(review.id, ReviewStatus.APPROVED):
                review.status = ReviewStatus.APPROVED
                review.save(update_fields=["status", "updated_at"])
                success_count += 1

        self.message_user(
            request,
            ngettext(
                "%d рецензия успешно одобрена и синхронизирована с Flask.",
                "%d рецензий успешно одобрено и синхронизировано с Flask.",
                success_count,
            )
            % success_count,
            messages.SUCCESS,
        )

    approve_reviews.description = "Одобрить выбранные рецензии"

    def hide_reviews(self, request, queryset):
        success_count = 0
        for review in queryset:
            if FlaskReviewsClient.send_status_update(review.id, ReviewStatus.HIDDEN):
                review.status = ReviewStatus.HIDDEN
                review.save(update_fields=["status", "updated_at"])
                success_count += 1

        self.message_user(
            request,
            ngettext(
                "%d рецензия успешно скрыта и синхронизирована с Flask.",
                "%d рецензий успешно скрыто и синхронизировано с Flask.",
                success_count,
            )
            % success_count,
            messages.SUCCESS,
        )

    hide_reviews.description = "Скрыть выбранные рецензии"
