from datetime import timedelta

from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required
from marshmallow import ValidationError

from ..extensions import db
from ..models.goal import Goal, GoalMilestone
from ..schemas.goal import (
    goal_create_schema,
    goal_milestone_patch_schema,
    goal_milestone_schema,
    goal_schema,
    goals_schema,
)
from .utils import error_response

goals_bp = Blueprint("goals", __name__, url_prefix="/api")

# design.md §7 は「未決事項」としてランキング集計を挙げているのみで、マイルストーンの
# デフォルトテンプレートは未定義。フロントと合意するまでの暫定値。
DEFAULT_MILESTONE_TEMPLATE = (
    {"title": "エントリーシート提出", "offset_days": -30},
    {"title": "一次面接", "offset_days": -14},
    {"title": "最終面接", "offset_days": -3},
)


@goals_bp.get("/goals")
@login_required
def list_goals():
    """
    ---
    get:
      summary: 自分の目標一覧を取得する
      security:
        - cookieAuth: []
      responses:
        200:
          description: 正常
          content:
            application/json:
              schema:
                type: array
                items: GoalSchema
        401:
          description: 未ログイン
    """
    goals = (
        Goal.query.filter(Goal.user_id == current_user.id)
        .order_by(Goal.target_date.asc())
        .all()
    )
    return jsonify(goals_schema.dump(goals)), 200


@goals_bp.post("/goals")
@login_required
def create_goal():
    """
    ---
    post:
      summary: 目標を作成する(マイルストーン自動生成込み)。user_idはクライアントから指定できない
      security:
        - cookieAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema: GoalCreateSchema
      responses:
        201:
          description: 作成成功
          content:
            application/json:
              schema: GoalSchema
        400:
          description: 入力エラー
        401:
          description: 未ログイン
    """
    payload = request.get_json(silent=True) or {}
    try:
        data = goal_create_schema.load(payload)
    except ValidationError as err:
        return error_response("validation_error", "入力内容を確認してください。", err.messages)

    milestone_inputs = data.pop("milestones", None) or DEFAULT_MILESTONE_TEMPLATE

    goal = Goal(user_id=current_user.id, **data)
    db.session.add(goal)
    db.session.flush()  # milestone 作成前に goal.id を確定させる

    for m in milestone_inputs:
        due_date = goal.target_date + timedelta(days=m["offset_days"])
        db.session.add(
            GoalMilestone(
                goal_id=goal.id,
                title=m["title"],
                due_date=due_date,
                offset_days=m["offset_days"],
            )
        )

    db.session.commit()
    return jsonify(goal_schema.dump(goal)), 201


@goals_bp.patch("/goals/<int:goal_id>/milestones/<int:milestone_id>")
@login_required
def update_milestone(goal_id, milestone_id):
    """
    ---
    patch:
      summary: 自分の目標のマイルストーン完了状態を切り替える。他人のマイルストーンは404
      security:
        - cookieAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema: GoalMilestonePatchSchema
      responses:
        200:
          description: 更新成功
          content:
            application/json:
              schema: GoalMilestoneSchema
        400:
          description: 入力エラー
        401:
          description: 未ログイン
        404:
          description: 存在しない、または他人のマイルストーン
    """
    payload = request.get_json(silent=True) or {}
    try:
        data = goal_milestone_patch_schema.load(payload)
    except ValidationError as err:
        return error_response("validation_error", "入力内容を確認してください。", err.messages)

    # 所有者確認はクエリ条件に含める(todos.py と同じパターン)。
    milestone = (
        GoalMilestone.query.join(Goal, GoalMilestone.goal_id == Goal.id)
        .filter(
            GoalMilestone.id == milestone_id,
            GoalMilestone.goal_id == goal_id,
            Goal.user_id == current_user.id,
        )
        .first()
    )
    if milestone is None:
        # 未存在／所有者不一致のどちらも 404 に統一(design.md §7: 権限なし → 404)。
        return error_response("not_found", "マイルストーンが見つかりません。", status=404)

    milestone.done = data["done"]
    db.session.commit()
    return jsonify(goal_milestone_schema.dump(milestone)), 200


@goals_bp.delete("/goals/<int:goal_id>")
@login_required
def delete_goal(goal_id):
    """
    ---
    delete:
      summary: 自分の目標を削除する。他人の目標は404
      security:
        - cookieAuth: []
      responses:
        204:
          description: 削除成功
        401:
          description: 未ログイン
        404:
          description: 存在しない、または他人の目標
    """
    goal = Goal.query.filter(Goal.id == goal_id, Goal.user_id == current_user.id).first()
    if goal is None:
        return error_response("not_found", "目標が見つかりません。", status=404)

    GoalMilestone.query.filter(GoalMilestone.goal_id == goal.id).delete()
    db.session.delete(goal)
    db.session.commit()
    return "", 204
