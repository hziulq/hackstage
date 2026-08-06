import os

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
login_manager = LoginManager()
limiter = Limiter(key_func=get_remote_address)

# migrations/ はリポジトリルート直下に置く(docs/design.md §3)。
# api コンテナには apps/api しかマウントされていないため、
# flask db コマンドは dev コンテナから実行する(CONTRIBUTING.md §5)。
_APPS_API_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_REPO_ROOT = os.path.dirname(os.path.dirname(_APPS_API_DIR))
MIGRATIONS_DIR = os.path.join(_REPO_ROOT, "migrations")

migrate = Migrate(directory=MIGRATIONS_DIR)
