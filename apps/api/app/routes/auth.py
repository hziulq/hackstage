from flask import Blueprint, jsonify, request, session
from flask_login import current_user, login_required, login_user, logout_user
from marshmallow import ValidationError

from ..extensions import db, limiter
from ..models import User
from ..schemas.user import login_schema, register_schema, user_schema

bp = Blueprint("auth", __name__, url_prefix="/api")


@bp.post("/register")
def register():
    """新規登録
    ---
    post:
      summary: オープン登録(認証不要)。メール重複は400
      requestBody:
        required: true
        content:
          application/json:
            schema: RegisterSchema
      responses:
        201:
          description: 登録成功
          content:
            application/json:
              schema: UserSchema
        400:
          description: 入力エラー、またはメール重複
    """
    try:
        data = register_schema.load(request.get_json(silent=True) or {})
    except ValidationError as err:
        return (
            jsonify({"error": {"code": "invalid_request", "message": "validation failed", "fields": err.messages}}),
            400,
        )

    if User.query.filter_by(email=data["email"]).first() is not None:
        return jsonify({"error": {"code": "invalid_request", "message": "email is already registered"}}), 400

    user = User(email=data["email"], display_name=data["display_name"])
    user.set_password(data["password"])
    db.session.add(user)
    db.session.commit()

    return jsonify(user_schema.dump(user)), 201


@bp.post("/login")
@limiter.limit("5 per minute")
def login():
    """ログイン
    ---
    post:
      summary: 認証してセッションCookieを発行する(認証不要)。試行はレート制限あり
      requestBody:
        required: true
        content:
          application/json:
            schema: LoginSchema
      responses:
        200:
          description: ログイン成功
          content:
            application/json:
              schema: UserSchema
        401:
          description: メール不存在・パスワード誤りを区別しない一律のエラー
        429:
          description: レート制限超過
    """
    try:
        data = login_schema.load(request.get_json(silent=True) or {})
    except ValidationError as err:
        return (
            jsonify({"error": {"code": "invalid_request", "message": "validation failed", "fields": err.messages}}),
            400,
        )

    # メール不存在とパスワード誤りを区別しない一律のエラーにする(FR-008)
    user = User.query.filter_by(email=data["email"]).first()
    if user is None or not user.check_password(data["password"]):
        return jsonify({"error": {"code": "invalid_credentials", "message": "email or password is incorrect"}}), 401

    session.permanent = True  # PERMANENT_SESSION_LIFETIME(7日, config.py)を有効にする
    login_user(user)

    return jsonify(user_schema.dump(user))


@bp.post("/logout")
@login_required
def logout():
    """ログアウト
    ---
    post:
      summary: セッションを破棄する
      security:
        - cookieAuth: []
      responses:
        204:
          description: ログアウト成功
        401:
          description: 未ログイン
    """
    logout_user()
    return "", 204


@bp.get("/me")
@login_required
def me():
    """自分の情報を取得
    ---
    get:
      summary: 現在のユーザー情報を取得する
      security:
        - cookieAuth: []
      responses:
        200:
          description: 正常
          content:
            application/json:
              schema: UserSchema
        401:
          description: 未ログイン
    """
    return jsonify(user_schema.dump(current_user))
