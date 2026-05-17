from api.v1.api import api_bp
from core.config import settings
from flask import Flask
from flask_migrate import Migrate
from reviews.exceptions_handler import register_error_handlers
from reviews.models import db


def create_app():
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = settings.SQLALCHEMY_DATABASE_URI
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    Migrate(app, db)

    register_error_handlers(app)

    app.register_blueprint(api_bp, url_prefix="/api/v1/reviews")

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5001, debug=True)  # noqa: S104
