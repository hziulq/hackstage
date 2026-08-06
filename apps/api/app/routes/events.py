from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required
from sqlalchemy import or_

from ..models.event import Event
from ..schemas.event import events_schema
from .utils import error_response, is_calendar_member

events_bp = Blueprint("events", __name__, url_prefix="/api")


@events_bp.get("/events")
@login_required
def list_events():
    """
    ---
    get:
      summary: カレンダーの予定一覧を取得する。参加者本人のみ。他人のis_private予定は含まれない
      security:
        - cookieAuth: []
      responses:
        200:
          description: 正常
          content:
            application/json:
              schema:
                type: array
                items: EventSchema
        401:
          description: 未ログイン
        404:
          description: 参加していないカレンダー
    """
    calendar_id = request.args.get("calendar_id", type=int)
    if calendar_id is None:
        return error_response(
            "missing_calendar_id",
            "calendar_id は必須です。",
            {"calendar_id": ["必須項目です。"]},
        )

    if not is_calendar_member(calendar_id, current_user.id):
        return error_response("not_found", "カレンダーが見つかりません。", status=404)

    # is_private な予定は本人以外に見せない(取得後のifではなくクエリ条件に含める、憲章 原則III)。
    events = (
        Event.query.filter(
            Event.calendar_id == calendar_id,
            or_(Event.is_private.is_(False), Event.user_id == current_user.id),
        )
        .order_by(Event.start_at.asc())
        .all()
    )
    return jsonify(events_schema.dump(events)), 200
