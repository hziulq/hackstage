from flask import Flask

from .config import Config


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    from .routes.health import bp as health_bp
    from .routes.hello import bp as hello_bp
    app.register_blueprint(health_bp)
    app.register_blueprint(hello_bp)

    return app
