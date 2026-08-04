from flask import Flask, jsonify

from .config import Config
from .extensions import db, migrate


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    from . import models  # noqa: F401  Alembic の autogenerate 用にモデルを登録する
    from app.models import dragon  # noqa

    from .routes.health import bp as health_bp
    from .routes.hello import bp as hello_bp
    from .routes.todos import bp as todos_bp
    from app.routes.dragon import dragon_bp
    app.register_blueprint(health_bp)
    app.register_blueprint(hello_bp)
    app.register_blueprint(todos_bp)
    app.register_blueprint(dragon_bp, url_prefix="/api/dragons")

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Not Found"}), 404

    return app
