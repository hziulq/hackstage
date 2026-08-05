from flask import Flask, jsonify

from .config import Config
from .extensions import db, limiter, login_manager, migrate


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    limiter.init_app(app)

    from . import models  # noqa: F401  Alembic の autogenerate 用にモデルを登録する
    from .models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # API専用バックエンドのためログイン画面へのリダイレクトではなくJSON 401を返す
    @login_manager.unauthorized_handler
    def unauthorized():
        return jsonify({"error": {"code": "unauthorized", "message": "login required"}}), 401

    from .routes.auth import bp as auth_bp
    from .routes.health import bp as health_bp
    from .routes.hello import bp as hello_bp
    from .routes.todos import (
        bp as todos_bp,  # feature/dragon-db-test の dragon_bp はTodoに移植して削除した
    )
    app.register_blueprint(auth_bp)
    from .routes.todos import bp as todos_bp  # feature/dragon-db-test の dragon_bp はTodoに移植して削除した
    from .routes.posts import posts_bp
    from .routes.goals import goals_bp
    from .routes.events import events_bp
    from .routes.reactions import reactions_bp
    from .routes.calendars import calendars_bp
    app.register_blueprint(health_bp)
    app.register_blueprint(hello_bp)
    app.register_blueprint(todos_bp)
    app.register_blueprint(posts_bp)
    app.register_blueprint(goals_bp)
    app.register_blueprint(events_bp)
    app.register_blueprint(reactions_bp)
    app.register_blueprint(calendars_bp)

    # 未知のルートに対するJSONの404(dragon-db-testのerrorhandlerを、
    # docs/design.md §7 のエラー形式 {"error": {"code", "message"}} に合わせて採用)
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": {"code": "not_found", "message": "Not Found"}}), 404

    return app
