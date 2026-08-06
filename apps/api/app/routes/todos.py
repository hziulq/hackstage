# kimuch-source さんの routes/dragon.py (56c9cac) をTodoモデル用に移植したもの。
# CRUDの構成・marshmallowでのバリデーションはそのまま。変えたのは主に2点:
#   1. Dragonには所有者がいなかったが、Todoは user_id を持つため、
#      get_or_404(id) だけでなく user_id もクエリ条件に含めている(下記参照)
#   2. エラー時のJSONの形を {"error": {"code", "message", ...}} に統一(docs/design.md §7)
from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required
from marshmallow import ValidationError

from ..extensions import db
from ..models import Todo
from ..schemas.todo import todo_schema, todos_schema

bp = Blueprint("todos", __name__, url_prefix="/api")


@bp.get("/todos")
@login_required
def list_todos():
    """Todo一覧
    ---
    get:
      summary: 自分のTodoの一覧を取得する
      security:
        - cookieAuth: []
      responses:
        200:
          description: 正常
          content:
            application/json:
              schema:
                type: array
                items: TodoSchema
        401:
          description: 未ログイン
    """
    todos = Todo.query.filter_by(user_id=current_user.id).order_by(Todo.id).all()
    return jsonify(todos_schema.dump(todos))


@bp.get("/todos/<int:todo_id>")
@login_required
def get_todo(todo_id):
    """Todo取得
    ---
    get:
      summary: 自分のTodoを1件取得する。他人のTodoは404
      security:
        - cookieAuth: []
      responses:
        200:
          description: 正常
          content:
            application/json:
              schema: TodoSchema
        401:
          description: 未ログイン
        404:
          description: 存在しない、または他人のTodo
    """
    # 所有者確認はクエリ条件に含める(憲章 原則III)。取得後に if で弾かない。
    todo = Todo.query.filter_by(id=todo_id, user_id=current_user.id).first()
    if todo is None:
        return jsonify({"error": {"code": "not_found", "message": "not found"}}), 404

    return jsonify(todo_schema.dump(todo))


@bp.post("/todos")
@login_required
def create_todo():
    """Todo作成
    ---
    post:
      summary: 自分のTodoを作成する。user_idはクライアントから指定できない
      security:
        - cookieAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema: TodoSchema
      responses:
        201:
          description: 作成成功
          content:
            application/json:
              schema: TodoSchema
        400:
          description: 入力エラー
        401:
          description: 未ログイン
    """
    try:
        data = todo_schema.load(request.get_json(silent=True) or {})
    except ValidationError as err:
        return (
            jsonify({"error": {"code": "invalid_request", "message": "validation failed", "fields": err.messages}}),
            400,
        )

    todo = Todo(user_id=current_user.id, title=data["title"], due_date=data.get("due_date"))
    db.session.add(todo)
    db.session.commit()

    return jsonify(todo_schema.dump(todo)), 201


@bp.put("/todos/<int:todo_id>")
@login_required
def update_todo(todo_id):
    """Todo更新
    ---
    put:
      summary: 自分のTodoを更新する。所有者の付け替えはできない
      security:
        - cookieAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema: TodoSchema
      responses:
        200:
          description: 更新成功
          content:
            application/json:
              schema: TodoSchema
        400:
          description: 入力エラー
        401:
          description: 未ログイン
        404:
          description: 存在しない、または他人のTodo
    """
    todo = Todo.query.filter_by(id=todo_id, user_id=current_user.id).first()
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
@login_required
def delete_todo(todo_id):
    """Todo削除
    ---
    delete:
      summary: 自分のTodoを削除する
      security:
        - cookieAuth: []
      responses:
        204:
          description: 削除成功
        401:
          description: 未ログイン
        404:
          description: 存在しない、または他人のTodo
    """
    todo = Todo.query.filter_by(id=todo_id, user_id=current_user.id).first()
    if todo is None:
        return jsonify({"error": {"code": "not_found", "message": "not found"}}), 404

    db.session.delete(todo)
    db.session.commit()

    return "", 204
