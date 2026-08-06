from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required
from marshmallow import ValidationError
from sqlalchemy import or_

from ..extensions import db
from ..models.event import Event
from ..schemas.event import event_schema, events_schema
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


@events_bp.post("/events")
@login_required
def create_event():
    """
    ---
    post:
      summary: 予定を作成する。user_idはクライアントから指定できない
      security:
        - cookieAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema: EventSchema
      responses:
        201:
          description: 作成成功
          content:
            application/json:
              schema: EventSchema
        400:
          description: 入力エラー
        401:
          description: 未ログイン
        404:
          description: 参加していないカレンダー
    """
    payload = request.get_json(silent=True) or {}
    try:
        data = event_schema.load(payload)
    except ValidationError as err:
        return error_response("validation_error", "入力内容を確認してください。", err.messages)

    if not is_calendar_member(data["calendar_id"], current_user.id):
        return error_response("not_found", "カレンダーが見つかりません。", status=404)

    event = Event(user_id=current_user.id, **data)
    db.session.add(event)
    db.session.commit()
    return jsonify(event_schema.dump(event)), 201
