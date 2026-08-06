from flask import Blueprint, jsonify, request
 
from flask import Blueprint, jsonify, request
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
def create_reaction():
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
        Reaction.user_id == data["user_id"],
        Reaction.target_type == data["target_type"],
        Reaction.target_id == data["target_id"],
    ).first()
 
    if existing is not None:
        # UniqueConstraint(user_id, target_type, target_id): 1人1対象1種類。
        # 既存レコードがあれば新規作成せず種類を上書きする（フロントの myReaction は単一値）。
        existing.kind = data["kind"]
        db.session.commit()
        return jsonify(reaction_schema.dump(existing)), 200
 
    reaction = Reaction(**data)
    db.session.add(reaction)
    db.session.commit()
    return jsonify(reaction_schema.dump(reaction)), 201
 
 
@reactions_bp.delete("/reactions/<int:reaction_id>")
def delete_reaction(reaction_id):
    user_id = request.args.get("user_id", type=int)
    if user_id is None:
        return error_response(
            "missing_user_id", "user_id は必須です。", {"user_id": ["必須項目です。"]}
        )
 
    reaction = Reaction.query.filter(
        Reaction.id == reaction_id, Reaction.user_id == user_id
    ).first()
    if reaction is None:
        return error_response("not_found", "リアクションが見つかりません。", status=404)
 
    db.session.delete(reaction)
    db.session.commit()
    return "", 204
