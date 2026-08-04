import os
from datetime import timedelta


class Config:
    SECRET_KEY = os.environ["SECRET_KEY"]

    DATABASE_URL = os.environ.get("DATABASE_URL")
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}

    # Cookie 属性は憲章 原則IV の必須値(docs/design.md §8)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = os.environ.get("SESSION_COOKIE_SECURE", "false").lower() == "true"
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
