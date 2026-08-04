from flask import Flask, jsonify

from .config import Config
from .extensions import db, migrate


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    from . import models  # noqa: F401  Alembic の autogenerate 用にモデルを登録する

    from .routes.health import bp as health_bp
    from .routes.hello import bp as hello_bp
    from .routes.todos import bp as todos_bp  # feature/dragon-db-test の dragon_bp はTodoに移植して削除した
    app.register_blueprint(health_bp)
    app.register_blueprint(hello_bp)
    app.register_blueprint(todos_bp)

    # 未知のルートに対するJSONの404(dragon-db-testのerrorhandlerを、
    # docs/design.md §7 のエラー形式 {"error": {"code", "message"}} に合わせて採用)
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": {"code": "not_found", "message": "Not Found"}}), 404

    return app
