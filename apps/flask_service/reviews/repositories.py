from datetime import UTC, datetime

from .errors import ForbiddenError, NotFoundError
from .models import Review, db


class ReviewRepository:
    def get_by_movie(self, movie_id: int, status: str = "approved") -> list[Review]:
        return (
            Review.query.filter_by(movie_id=movie_id, status=status, deleted_at=None)
            .order_by(Review.created_at.desc())
            .all()
        )

    def get_by_id(self, review_id: int) -> Review | None:
        return Review.query.filter_by(id=review_id, deleted_at=None).first()

    def get_user_review_for_movie(self, user_id: int, movie_id: int) -> Review | None:
        return Review.query.filter_by(
            user_id=user_id, movie_id=movie_id, deleted_at=None
        ).first()

    def create(self, data: dict) -> Review:
        review = Review(**data)
        db.session.add(review)
        db.session.flush()
        return review

    def create_with_moderation(self, data: dict, notify_func) -> Review:
        try:
            review = self.create(data)
            notify_func(review)
            db.session.commit()
            db.session.refresh(review)
            return review
        except Exception:
            db.session.rollback()
            raise

    def update_review_fields(
        self, review: Review, text: str | None = None, rating: int | None = None
    ) -> Review:
        if text is not None:
            review.text = text
        if rating is not None:
            review.rating = rating
        review.status = "pending"
        review.updated_at = datetime.now(UTC)
        db.session.flush()
        return review

    def update_with_moderation(
        self,
        review_id: int,
        user_id: int,
        notify_func,
        text: str | None = None,
        rating: int | None = None,
    ) -> Review:
        review = self.get_by_id(review_id)
        if not review:
            raise NotFoundError("Рецензия не найдена")
        if review.user_id != user_id:
            raise ForbiddenError("Вы не можете редактировать чужой отзыв")

        if text is not None:
            review.text = text
        if rating is not None:
            review.rating = rating
        review.status = "pending"
        review.updated_at = datetime.now(UTC)

        db.session.flush()

        try:
            notify_func(review)
            db.session.commit()
            db.session.refresh(review)
            return review
        except Exception:
            db.session.rollback()
            raise

    def update(self, review: Review, data: dict) -> Review:
        allowed_keys = {"text", "rating", "status"}
        for key, value in data.items():
            if key in allowed_keys:
                setattr(review, key, value)
        review.updated_at = datetime.now(UTC)
        db.session.commit()
        return review

    def soft_delete(self, review: Review) -> None:
        review.deleted_at = datetime.now(UTC)
        db.session.commit()
