from reviews.models import Review


class ReviewRepository:
    def get_by_id(self, review_id: int) -> Review | None:
        try:
            return Review.objects.get(id=review_id)
        except Review.DoesNotExist:
            return None

    def update_or_create_review(self, review_id: int, defaults: dict) -> Review:
        review, _ = Review.objects.update_or_create(id=review_id, defaults=defaults)
        return review
