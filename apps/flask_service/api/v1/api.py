from flask import Blueprint, jsonify, request
from reviews.auth import token_required
from reviews.schemas import ReviewCreateSchema, ReviewPublicSchema, ReviewUpdateSchema
from reviews.services import ReviewService

api_bp = Blueprint("api", __name__)
service = ReviewService()

create_schema = ReviewCreateSchema()
update_schema = ReviewUpdateSchema()
public_schema = ReviewPublicSchema()
list_schema = ReviewPublicSchema(many=True)


@api_bp.route("/movies/<int:movie_id>/reviews", methods=["POST"])
@token_required
def add_review(movie_id, user_id):
    data = create_schema.load(request.json)

    review = service.create_review(
        user_id=user_id, movie_id=movie_id, text=data["text"], rating=data["rating"]
    )
    return jsonify(public_schema.dump(review)), 201


@api_bp.route("/movies/<int:movie_id>/reviews", methods=["GET"])
def get_reviews(movie_id):
    reviews = service.get_movie_reviews(movie_id)
    return jsonify(list_schema.dump(reviews)), 200


@api_bp.route("/reviews/<int:review_id>", methods=["PUT"])
@token_required
def update_review(review_id, user_id):
    data = update_schema.load(request.json, partial=True)

    review = service.update_review(
        review_id=review_id,
        user_id=user_id,
        text=data.get("text"),
        rating=data.get("rating"),
    )
    return jsonify(public_schema.dump(review)), 200


@api_bp.route("/reviews/<int:review_id>", methods=["DELETE"])
@token_required
def delete_review(review_id, user_id):
    service.delete_review(review_id, user_id)
    return "", 204


@api_bp.route("/internal/reviews/<int:review_id>/status", methods=["PATCH"])
def change_status(review_id):
    from core.config import settings

    token = request.headers.get("X-Internal-Token")
    if token != settings.INTERNAL_SERVICE_TOKEN:
        return jsonify({"status": "error", "message": "Forbidden"}), 403

    data = request.json
    status = data.get("status")

    updated_review = service.change_review_status(review_id, status)
    return jsonify({"status": "success", "new_status": updated_review.status}), 200
