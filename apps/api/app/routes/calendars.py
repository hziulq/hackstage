from flask import Blueprint, jsonify, request
from sqlalchemy import func
 
from ..extensions import db
from ..models.calendar import Calendar, CalendarMember
from ..models.score import PointEvent
from ..models.user import User
from ..schemas.calendar import calendar_schema
from .utils import error_response
 
calendars_bp = Blueprint("calendars", __name__, url_prefix="/api")
 
 
@calendars_bp.get("/calendars/<int:calendar_id>")
def get_calendar(calendar_id):
    calendar = Calendar.query.get(calendar_id)
    if calendar is None:
        return error_response("not_found", "カレンダーが見つかりません。", status=404)
    return jsonify(calendar_schema.dump(calendar)), 200
 
 
@calendars_bp.get("/calendars/<int:calendar_id>/members")
def list_calendar_members(calendar_id):
    """
    GET /api/calendars/<id>/members?sort=score
 
    point_events はユーザー単位（calendar 単位ではない）のため、このカレンダーの
    メンバーそれぞれについて全期間の合計ポイントを集計してランキングする。
    集計方法・期間・並び順の正式仕様は design.md §7 の「未決事項」であり、暫定実装。
    """
    calendar = Calendar.query.get(calendar_id)
    if calendar is None:
        return error_response("not_found", "カレンダーが見つかりません。", status=404)
 
    points_subq = (
        db.session.query(
            PointEvent.user_id.label("user_id"),
            func.coalesce(func.sum(PointEvent.points), 0).label("total_points"),
        )
        .group_by(PointEvent.user_id)
        .subquery()
    )
    total_points_col = func.coalesce(points_subq.c.total_points, 0)
 
    rows_query = (
        db.session.query(
            CalendarMember.id,
            CalendarMember.user_id,
            CalendarMember.role,
            CalendarMember.joined_at,
            User.display_name,
            User.avatar_url,
            total_points_col.label("total_points"),
        )
        .join(User, CalendarMember.user_id == User.id)
        .outerjoin(points_subq, points_subq.c.user_id == CalendarMember.user_id)
        .filter(CalendarMember.calendar_id == calendar_id)
    )
 
    if request.args.get("sort") == "score":
        rows_query = rows_query.order_by(total_points_col.desc())
    else:
        rows_query = rows_query.order_by(CalendarMember.joined_at.asc())
 
    members = [
        {
            "id": row.id,
            "user_id": row.user_id,
            "role": row.role,
            "joined_at": row.joined_at.isoformat() if row.joined_at else None,
            "display_name": row.display_name,
            "avatar_url": row.avatar_url,
            "total_points": int(row.total_points),
        }
        for row in rows_query.all()
    ]
    return jsonify(members), 200
