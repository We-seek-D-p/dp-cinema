import httpx
from core.config import settings

from reviews.models import Review

from .errors import (
    ConflictError,
    DependencyError,
    ForbiddenError,
    NotFoundError,
    ValidationError,
)
from .repositories import ReviewRepository


def _verify_movie_exists(movie_id: int) -> bool:
    url = f"{settings.DJANGO_API_URL}/api/v1/movies/{movie_id}/"
    headers = {"X-Internal-Token": settings.INTERNAL_SERVICE_TOKEN}
    try:
        with httpx.Client(timeout=3.0) as client:
            response = client.get(url, headers=headers)
        if response.status_code == 404:
            return False
        if response.status_code == 200:
            return True
        raise DependencyError(f"Django API вернул ошибку: {response.status_code}")

    except httpx.RequestError as err:
        raise DependencyError(f"Не удалось связаться с Django: {str(err)}") from err


def _notify_moderation(review) -> None:
    url = f"{settings.DJANGO_API_URL}/api/v1/reviews/moderation/"
    headers = {"X-Internal-Token": settings.INTERNAL_SERVICE_TOKEN}

    payload = {
        "review_id": review.id,
        "movie_id": review.movie_id,
        "text": review.text,
        "rating": review.rating,
        "user_id": review.user_id,
    }

    try:
        with httpx.Client(timeout=2.0) as client:
            resp = client.post(url, json=payload, headers=headers)
            if resp.status_code not in (200, 201, 204):
                raise DependencyError(
                    f"Не удалось отправить запрос на модерацию: {resp.status_code}"
                )
    except Exception as err:
        raise DependencyError(
            f"Ошибка подключения во время запроса на модерацию: {str(err)}"
        ) from err


class ReviewService:
    def __init__(self):
        self.repo = ReviewRepository()

    def create_review(
        self, user_id: int, movie_id: int, text: str, rating: int
    ) -> Review:
        if self.repo.get_user_review_for_movie(user_id, movie_id):
            raise ConflictError("Вы уже оставили отзыв на этот фильм")

        if not _verify_movie_exists(movie_id):
            raise NotFoundError("Фильм не найден в каталоге Django")

        return self.repo.create_with_moderation(
            data={
                "user_id": user_id,
                "movie_id": movie_id,
                "text": text,
                "rating": rating,
                "status": "pending",
            },
            notify_func=_notify_moderation,
        )

    def update_review(
        self,
        review_id: int,
        user_id: int,
        text: str | None = None,
        rating: int | None = None,
    ) -> Review:
        if text is None and rating is None:
            raise ValidationError("Не передано ни одного поля для обновления")

        return self.repo.update_with_moderation(
            review_id=review_id,
            user_id=user_id,
            text=text,
            rating=rating,
            notify_func=_notify_moderation,
        )

    def change_review_status(self, review_id: int, status: str):
        review = self.repo.get_by_id(review_id)
        if not review:
            raise NotFoundError("Рецензия не найдена")

        valid_statuses = ["approved", "hidden", "pending"]
        if status not in valid_statuses:
            raise ValidationError(f"Недопустимый статус. Можно: {valid_statuses}")

        return self.repo.update(review, {"status": status})

    def delete_review(self, review_id: int, user_id: int):
        review = self.repo.get_by_id(review_id)
        if not review:
            raise NotFoundError("Рецензия не найдена")

        if review.user_id != user_id:
            raise ForbiddenError("Вы не можете удалить чужой отзыв")

        return self.repo.soft_delete(review)

    def get_movie_reviews(self, movie_id: int) -> list[Review]:
        return self.repo.get_by_movie(movie_id, status="approved")
