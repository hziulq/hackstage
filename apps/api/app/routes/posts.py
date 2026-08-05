from flask import Blueprint, jsonify, request
from marshmallow import ValidationError

from ..extensions import db
from ..models.board import POST_CATEGORIES, Post, PostComment
from ..models.calendar import Calendar
from ..schemas.post import post_comment_schema, post_schema, posts_schema
from .utils import error_response

posts_bp = Blueprint("posts", __name__, url_prefix="/api")

# 匿名表示の対象カテゴリ。モデルコメントのとおり、匿名化は API 層（レスポンス生成時）の責務。
_ANONYMOUS_CATEGORIES = {"anonymous_qa"}


def _serialize_post(post):
    data = post_schema.dump(post)
    #匿名表示
    if post.category in _ANONYMOUS_CATEGORIES:
        data["user_id"] = None
    return data


@posts_bp.get("/posts")
def list_posts():
    """
    GET /api/posts?category=...&tag=...&prefecture_id=...&calendar_id=...&scope=group|personal

    - Board: ?category=anonymous_qa&tag=...
    - Timeline: ?category=timeline&scope=group|personal
    - Mypage: ?category=prefecture_intern_info&prefecture_id=...
    のいずれの画面からも同じエンドポイントを共有する。
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
def create_post():
    payload = request.get_json(silent=True) or {}
    try:
        data = post_schema.load(payload)
    except ValidationError as err:
        return error_response("validation_error", "入力内容を確認してください。", err.messages)

    # timeline 投稿は calendar_id 必須（group/personal の判定に使うため）。
    if data["category"] == "timeline" and data.get("calendar_id") is None:
        return error_response(
            "validation_error",
            "入力内容を確認してください。",
            {"calendar_id": ["timeline 投稿には calendar_id が必須です。"]},
        )

    post = Post(**data)
    db.session.add(post)
    db.session.commit()
    return jsonify(_serialize_post(post)), 201


@posts_bp.post("/posts/<int:post_id>/comments")
def create_post_comment(post_id):
    post = Post.query.get(post_id)
    if post is None:
        return error_response("not_found", "投稿が見つかりません。", status=404)

    payload = request.get_json(silent=True) or {}
    try:
        data = post_comment_schema.load(payload)
    except ValidationError as err:
        return error_response("validation_error", "入力内容を確認してください。", err.messages)

    comment = PostComment(post_id=post_id, **data)
    db.session.add(comment)
    db.session.commit()
    return jsonify(post_comment_schema.dump(comment)), 201
