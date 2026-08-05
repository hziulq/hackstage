from datetime import timedelta

from flask import Blueprint, jsonify, request
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
def list_goals():
    user_id = request.args.get("user_id", type=int)
    if user_id is None:
        return error_response(
            "missing_user_id", "user_id は必須です。", {"user_id": ["必須項目です。"]}
        )

    goals = Goal.query.filter(Goal.user_id == user_id).order_by(Goal.target_date.asc()).all()
    return jsonify(goals_schema.dump(goals)), 200


@goals_bp.post("/goals")
def create_goal():
    payload = request.get_json(silent=True) or {}
    try:
        data = goal_create_schema.load(payload)
    except ValidationError as err:
        return error_response("validation_error", "入力内容を確認してください。", err.messages)

    milestone_inputs = data.pop("milestones", None) or DEFAULT_MILESTONE_TEMPLATE

    goal = Goal(**data)
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
def update_milestone(goal_id, milestone_id):
    user_id = request.args.get("user_id", type=int)
    if user_id is None:
        return error_response(
            "missing_user_id", "user_id は必須です。", {"user_id": ["必須項目です。"]}
        )

    payload = request.get_json(silent=True) or {}
    try:
        data = goal_milestone_patch_schema.load(payload)
    except ValidationError as err:
        return error_response("validation_error", "入力内容を確認してください。", err.messages)

    # 所有者確認はクエリ条件に含める（todos.py と同じパターン）。
    milestone = (
        GoalMilestone.query.join(Goal, GoalMilestone.goal_id == Goal.id)
        .filter(
            GoalMilestone.id == milestone_id,
            GoalMilestone.goal_id == goal_id,
            Goal.user_id == user_id,
        )
        .first()
    )
    if milestone is None:
        # 未存在／所有者不一致のどちらも 404 に統一（design.md §7: 権限なし → 404）。
        return error_response("not_found", "マイルストーンが見つかりません。", status=404)

    milestone.done = data["done"]
    db.session.commit()
    return jsonify(goal_milestone_schema.dump(milestone)), 200


@goals_bp.delete("/goals/<int:goal_id>")
def delete_goal(goal_id):
    user_id = request.args.get("user_id", type=int)
    if user_id is None:
        return error_response(
            "missing_user_id", "user_id は必須です。", {"user_id": ["必須項目です。"]}
        )

    goal = Goal.query.filter(Goal.id == goal_id, Goal.user_id == user_id).first()
    if goal is None:
        return error_response("not_found", "目標が見つかりません。", status=404)

    GoalMilestone.query.filter(GoalMilestone.goal_id == goal.id).delete()
    db.session.delete(goal)
    db.session.commit()
    return "", 204
