from datetime import UTC, datetime

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
