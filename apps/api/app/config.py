import os
from datetime import timedelta


class Config:
    SECRET_KEY = os.environ["SECRET_KEY"]

    # DB へ実際に接続する処理(SQLAlchemy 等)はまだ入れていない。
    # 値はここから読める状態にしてあるので、ライブラリを requirements.txt に
    # 追加した後にそのまま使える(接続方法は README.md 参照)。
    DATABASE_URL = os.environ.get("DATABASE_URL")

    # Cookie 属性は憲章 原則IV の必須値(docs/design.md §8)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = os.environ.get("SESSION_COOKIE_SECURE", "false").lower() == "true"
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
