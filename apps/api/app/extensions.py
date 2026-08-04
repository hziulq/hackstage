import os

from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# feature/dragon-db-test にあった login_manager はここでは持たない。
# 認証(Flask-Login)は 003-user-auth 側で別途追加する予定。

# migrations/ はリポジトリルート直下に置く(docs/design.md §3)。
# api コンテナには apps/api しかマウントされていないため、
# flask db コマンドは dev コンテナから実行する(CONTRIBUTING.md §5)。
_APPS_API_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_REPO_ROOT = os.path.dirname(os.path.dirname(_APPS_API_DIR))
MIGRATIONS_DIR = os.path.join(_REPO_ROOT, "migrations")

migrate = Migrate(directory=MIGRATIONS_DIR)
