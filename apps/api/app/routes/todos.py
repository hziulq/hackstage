# kimuch-source さんの routes/dragon.py (56c9cac) をTodoモデル用に移植したもの。
# CRUDの構成・marshmallowでのバリデーションはそのまま。変えたのは主に2点:
#   1. Dragonには所有者がいなかったが、Todoは user_id を持つため、
#      get_or_404(id) だけでなく user_id もクエリ条件に含めている(下記参照)
#   2. エラー時のJSONの形を {"error": {"code", "message", ...}} に統一(docs/design.md §7)
from flask import Blueprint, jsonify, request
from marshmallow import ValidationError

from ..extensions import db
from ..models import Todo
from ..schemas.todo import todo_schema, todos_schema

bp = Blueprint("todos", __name__, url_prefix="/api")


@bp.get("/todos")
def list_todos():
    # 本来は current_user.id を使う(憲章 原則III)。Flask-Login 未導入のため
    # 学習用の暫定実装としてクエリパラメータで受け取っている。
    user_id = request.args.get("user_id", type=int)
    if user_id is None:
        return jsonify({"error": {"code": "invalid_request", "message": "user_id is required"}}), 400

    todos = Todo.query.filter_by(user_id=user_id).order_by(Todo.id).all()
    return jsonify(todos_schema.dump(todos))


@bp.get("/todos/<int:todo_id>")
def get_todo(todo_id):
    user_id = request.args.get("user_id", type=int)
    # 所有者確認はクエリ条件に含める(憲章 原則III)。取得後に if で弾かない。
    todo = Todo.query.filter_by(id=todo_id, user_id=user_id).first()
    if todo is None:
        return jsonify({"error": {"code": "not_found", "message": "not found"}}), 404

    return jsonify(todo_schema.dump(todo))


@bp.post("/todos")
def create_todo():
    try:
        data = todo_schema.load(request.get_json(silent=True) or {})
    except ValidationError as err:
        return (
            jsonify({"error": {"code": "invalid_request", "message": "validation failed", "fields": err.messages}}),
            400,
        )

    todo = Todo(user_id=data["user_id"], title=data["title"], due_date=data.get("due_date"))
    db.session.add(todo)
    db.session.commit()

    return jsonify(todo_schema.dump(todo)), 201


@bp.put("/todos/<int:todo_id>")
def update_todo(todo_id):
    user_id = request.args.get("user_id", type=int)
    todo = Todo.query.filter_by(id=todo_id, user_id=user_id).first()
    if todo is None:
        return jsonify({"error": {"code": "not_found", "message": "not found"}}), 404

    try:
        data = todo_schema.load(request.get_json(silent=True) or {}, partial=True)
    except ValidationError as err:
        return (
            jsonify({"error": {"code": "invalid_request", "message": "validation failed", "fields": err.messages}}),
            400,
        )

    for key, value in data.items():
        if key == "user_id":
            continue  # 所有者の付け替えはさせない
        setattr(todo, key, value)
    db.session.commit()

    return jsonify(todo_schema.dump(todo))


@bp.delete("/todos/<int:todo_id>")
def delete_todo(todo_id):
    user_id = request.args.get("user_id", type=int)
    todo = Todo.query.filter_by(id=todo_id, user_id=user_id).first()
    if todo is None:
        return jsonify({"error": {"code": "not_found", "message": "not found"}}), 404

    db.session.delete(todo)
    db.session.commit()

    return "", 204
