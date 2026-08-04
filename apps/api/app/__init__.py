from flask import Flask

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
    from .routes.todos import bp as todos_bp
    app.register_blueprint(health_bp)
    app.register_blueprint(hello_bp)
    app.register_blueprint(todos_bp)

    return app
