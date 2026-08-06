from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required
from marshmallow import ValidationError

from ..extensions import db
from ..models.board import Post
from ..models.event import Event
from ..models.reaction import Reaction
from ..schemas.reaction import reaction_schema
from .utils import error_response

reactions_bp = Blueprint("reactions", __name__, url_prefix="/api")

_TARGET_MODELS = {"event": Event, "post": Post}


@reactions_bp.post("/reactions")
@login_required
def create_reaction():
    """
    ---
    post:
      summary: リアクションを追加する。user_idはクライアントから指定できない
      security:
        - cookieAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema: ReactionSchema
      responses:
        201:
          description: 作成成功
          content:
            application/json:
              schema: ReactionSchema
        200:
          description: 既存のリアクションのkindを上書き
          content:
            application/json:
              schema: ReactionSchema
        400:
          description: 入力エラー
        401:
          description: 未ログイン
        404:
          description: 対象が存在しない
    """
    payload = request.get_json(silent=True) or {}
    try:
        data = reaction_schema.load(payload)
    except ValidationError as err:
        return error_response("validation_error", "入力内容を確認してください。", err.messages)

    target_model = _TARGET_MODELS[data["target_type"]]
    target = target_model.query.get(data["target_id"])
    if target is None:
        return error_response("not_found", "対象が見つかりません。", status=404)

    existing = Reaction.query.filter(
        Reaction.user_id == current_user.id,
        Reaction.target_type == data["target_type"],
        Reaction.target_id == data["target_id"],
    ).first()

    if existing is not None:
        # UniqueConstraint(user_id, target_type, target_id): 1人1対象1種類。
        # 既存レコードがあれば新規作成せず種類を上書きする(フロントのmyReactionは単一値)。
        existing.kind = data["kind"]
        db.session.commit()
        return jsonify(reaction_schema.dump(existing)), 200

    reaction = Reaction(user_id=current_user.id, **data)
    db.session.add(reaction)
    db.session.commit()
    return jsonify(reaction_schema.dump(reaction)), 201


@reactions_bp.delete("/reactions/<int:reaction_id>")
@login_required
def delete_reaction(reaction_id):
    """
    ---
    delete:
      summary: 自分のリアクションを削除する。他人のリアクションは404
      security:
        - cookieAuth: []
      responses:
        204:
          description: 削除成功
        401:
          description: 未ログイン
        404:
          description: 存在しない、または他人のリアクション
    """
    # 所有者確認はクエリ条件に含める(憲章 原則III)。取得後にifで弾かない。
    reaction = Reaction.query.filter(
        Reaction.id == reaction_id, Reaction.user_id == current_user.id
    ).first()
    if reaction is None:
        return error_response("not_found", "リアクションが見つかりません。", status=404)

    db.session.delete(reaction)
    db.session.commit()
    return "", 204
