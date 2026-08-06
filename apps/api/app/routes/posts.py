from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required
from marshmallow import ValidationError

from ..extensions import db
from ..models.board import POST_CATEGORIES, Post, PostComment
from ..models.calendar import Calendar
from ..schemas.post import (
    post_comment_schema,
    post_comments_schema,
    post_schema,
)
from .utils import error_response, is_calendar_member

posts_bp = Blueprint("posts", __name__, url_prefix="/api")

# 匿名表示の対象カテゴリ。モデルコメントのとおり、匿名化は API 層(レスポンス生成時)の責務。
_ANONYMOUS_CATEGORIES = {"anonymous_qa"}


def _serialize_post(post):
    data = post_schema.dump(post)
    #匿名表示
    if post.category in _ANONYMOUS_CATEGORIES:
        data["user_id"] = None
    return data


@posts_bp.get("/posts")
@login_required
def list_posts():
    """
    GET /api/posts?category=...&tag=...&prefecture_id=...&calendar_id=...&scope=group|personal

    - Board: ?category=anonymous_qa&tag=...
    - Timeline: ?category=timeline&scope=group|personal
    - Mypage: ?category=prefecture_intern_info&prefecture_id=...
    のいずれの画面からも同じエンドポイントを共有する。
    ---
    get:
      summary: 投稿一覧を取得する。calendar_id指定時は参加者本人のみ
      security:
        - cookieAuth: []
      responses:
        200:
          description: 正常
          content:
            application/json:
              schema:
                type: array
                items: PostSchema
        401:
          description: 未ログイン
        404:
          description: calendar_id指定時、参加していないカレンダー
    """
    query = Post.query

    category = request.args.get("category")
    if category is not None:
        if category not in POST_CATEGORIES:
            return error_response(
                "invalid_category",
                "category が不正です。",
                {"category": [f"'{category}' は許可されていません。"]},
            )
        query = query.filter(Post.category == category)

    tag = request.args.get("tag")
    if tag:
        query = query.filter(Post.tags.any(tag))

    prefecture_id = request.args.get("prefecture_id", type=int)
    if prefecture_id is not None:
        query = query.filter(Post.prefecture_id == prefecture_id)

    calendar_id = request.args.get("calendar_id", type=int)
    if calendar_id is not None:
        # 参加していないカレンダーの投稿は見せない(他人の個人/グループカレンダーの漏洩防止)。
        if not is_calendar_member(calendar_id, current_user.id):
            return error_response("not_found", "カレンダーが見つかりません。", status=404)
        query = query.filter(Post.calendar_id == calendar_id)

    scope = request.args.get("scope")
    if scope is not None:
        if scope not in ("group", "personal"):
            return error_response(
                "invalid_scope",
                "scope が不正です。",
                {"scope": ["'group' または 'personal' を指定してください。"]},
            )
        query = query.join(Calendar, Post.calendar_id == Calendar.id).filter(
            Calendar.type == scope
        )

    posts = query.order_by(Post.created_at.desc()).all()
    return jsonify([_serialize_post(post) for post in posts]), 200


@posts_bp.post("/posts")
@login_required
def create_post():
    """
    ---
    post:
      summary: 投稿を作成する。user_idはクライアントから指定できない
      security:
        - cookieAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema: PostSchema
      responses:
        201:
          description: 作成成功
          content:
            application/json:
              schema: PostSchema
        400:
          description: 入力エラー
        401:
          description: 未ログイン
        404:
          description: calendar_id指定時、参加していないカレンダー
    """
    payload = request.get_json(silent=True) or {}
    try:
        data = post_schema.load(payload)
    except ValidationError as err:
        return error_response("validation_error", "入力内容を確認してください。", err.messages)

    # timeline 投稿は calendar_id 必須(group/personal の判定に使うため)。
    if data["category"] == "timeline" and data.get("calendar_id") is None:
        return error_response(
            "validation_error",
            "入力内容を確認してください。",
            {"calendar_id": ["timeline 投稿には calendar_id が必須です。"]},
        )

    calendar_id = data.get("calendar_id")
    if calendar_id is not None and not is_calendar_member(calendar_id, current_user.id):
        return error_response("not_found", "カレンダーが見つかりません。", status=404)

    post = Post(user_id=current_user.id, **data)
    db.session.add(post)
    db.session.commit()
    return jsonify(_serialize_post(post)), 201


@posts_bp.get("/posts/<int:post_id>/comments")
@login_required
def list_post_comments(post_id):
    """
    ---
    get:
      summary: 投稿のコメント一覧を取得する
      security:
        - cookieAuth: []
      responses:
        200:
          description: 正常
          content:
            application/json:
              schema:
                type: array
                items: PostCommentSchema
        401:
          description: 未ログイン
        404:
          description: 対象の投稿が存在しない
    """
    post = Post.query.get(post_id)
    if post is None:
        return error_response("not_found", "投稿が見つかりません。", status=404)

    comments = (
        PostComment.query.filter_by(post_id=post_id).order_by(PostComment.created_at.asc()).all()
    )
    return jsonify(post_comments_schema.dump(comments)), 200


@posts_bp.post("/posts/<int:post_id>/comments")
@login_required
def create_post_comment(post_id):
    """
    ---
    post:
      summary: 投稿にコメントを追加する。user_idはクライアントから指定できない
      security:
        - cookieAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema: PostCommentSchema
      responses:
        201:
          description: 作成成功
          content:
            application/json:
              schema: PostCommentSchema
        400:
          description: 入力エラー
        401:
          description: 未ログイン
        404:
          description: 対象の投稿が存在しない
    """
    post = Post.query.get(post_id)
    if post is None:
        return error_response("not_found", "投稿が見つかりません。", status=404)

    payload = request.get_json(silent=True) or {}
    try:
        data = post_comment_schema.load(payload)
    except ValidationError as err:
        return error_response("validation_error", "入力内容を確認してください。", err.messages)

    comment = PostComment(post_id=post_id, user_id=current_user.id, **data)
    db.session.add(comment)
    db.session.commit()
    return jsonify(post_comment_schema.dump(comment)), 201
