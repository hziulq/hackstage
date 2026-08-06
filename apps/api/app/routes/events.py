from flask import Blueprint, jsonify, request
 
from ..models.event import Event
from ..schemas.event import events_schema
from .utils import error_response
 
events_bp = Blueprint("events", __name__, url_prefix="/api")
 
 
@events_bp.get("/events")
def list_events():
    calendar_id = request.args.get("calendar_id", type=int)
    if calendar_id is None:
        return error_response(
            "missing_calendar_id",
            "calendar_id は必須です。",
            {"calendar_id": ["必須項目です。"]},
        )
 
    # TODO: 認証実装後、current_user.id を用いて is_private な予定は本人以外に見せないよう
    # 絞り込みを追加する（現状は calendar_id が一致すれば全件返す）。
    events = (
        Event.query.filter(Event.calendar_id == calendar_id).order_by(Event.start_at.asc()).all()
    )
    return jsonify(events_schema.dump(events)), 200
