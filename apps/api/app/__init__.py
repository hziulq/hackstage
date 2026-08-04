# import os
# from flask import Flask, jsonify
# from app.config import config_map
# from app.extensions import db, migrate, login_manager


# def create_app():
#     app = Flask(__name__)

#     env = os.environ.get("FLASK_ENV")
#     app.config.from_object(config_map[env])

#     # 拡張の初期化
#     db.init_app(app)
#     migrate.init_app(app, db)
#     login_manager.init_app(app)

#     # モデルをimportしてマイグレーション対象に含める
#     from app.models import user  # noqa

#     # Blueprint登録
#     from app.routes.user import user_bp
#     app.register_blueprint(user_bp, url_prefix="/api/users")

#     # 共通エラーハンドラ（全レスポンスJSON統一）
#     @app.errorhandler(404)
#     def not_found(e):
#         return jsonify({"error": "Not Found"}), 404

#     @app.errorhandler(500)
#     def server_error(e):
#         return jsonify({"error": "Internal Server Error"}), 500

#     return app


from flask import Flask, jsonify
from app.config import Config
from app.extensions import db, migrate


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    from app.models import dragon  # noqa

    from app.routes.dragon import dragon_bp
    app.register_blueprint(dragon_bp, url_prefix="/api/dragons")

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Not Found"}), 404

    return app