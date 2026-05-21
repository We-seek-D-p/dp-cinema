import httpx
from django.conf import settings
from rest_framework.exceptions import ValidationError
from movies.repositories import MovieRepository
from reviews.models import Review, ReviewStatus
from reviews.repositories import ReviewRepository


class FlaskReviewsClient:
    @staticmethod
    def send_status_update(review_id: int, status: str) -> bool:
        url = f"{settings.FLASK_SERVICE_URL}/api/v1/internal/reviews/{review_id}/status"
        headers = {"X-Internal-Token": settings.INTERNAL_SERVICE_TOKEN}
        payload = {"status": status}
        try:
            with httpx.Client(timeout=3.0) as client:
                response = client.patch(url, json=payload, headers=headers)
                
                if response.status_code == 200:
                    return True
                return False
        except httpx.RequestError as exc:
            return False


class ReviewModerationService:
    def __init__(self) -> None:
        self.movie_repo = MovieRepository()
        self.review_repo = ReviewRepository()

    def handle_incoming_review(self, data: dict) -> Review:
        movie_id = data["movie_id"]
        movie_exists = self.movie_repo.get_active().filter(id=movie_id).exists()

        if not movie_exists:
            raise ValidationError({"movie_id": "Фильм не найден в каталоге Django"})

        review_data = {
            "movie_id": movie_id,
            "user_id": data["user_id"],
            "text": data["text"],
            "rating": data["rating"],
            "status": ReviewStatus.PENDING,
        }

        return self.review_repo.update_or_create_review(
            review_id=data["review_id"],
            defaults=review_data,
        )
