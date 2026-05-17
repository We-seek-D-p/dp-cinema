from flask import jsonify
from marshmallow import ValidationError as MarshmallowValidationError

from reviews.errors import ReviewError


def register_error_handlers(app):
    @app.errorhandler(ReviewError)
    def handle_review_error(error):
        return jsonify({"status": "error", "message": error.message}), error.status_code

    @app.errorhandler(MarshmallowValidationError)
    def handle_marshmallow_validation(err):
        return jsonify(
            {
                "status": "error",
                "message": "Ошибка валидации данных",
                "details": err.messages,
            }
        ), 400

    @app.errorhandler(Exception)
    def handle_unexpected_error(e):
        return jsonify(
            {"status": "error", "message": "Произошла непредвиденная ошибка на сервере"}
        ), 500
