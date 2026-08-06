from flask import jsonify

from ..models.calendar import CalendarMember


def error_response(code, message, fields=None, status=400):
    """design.md §7 のエラー契約に合わせた統一フォーマット。

    {"error": {"code": "...", "message": "...", "fields": {...}}}
    """
    body = {"error": {"code": code, "message": message}}
    if fields:
        body["error"]["fields"] = fields
    return jsonify(body), status


def is_calendar_member(calendar_id, user_id):
    """current_user が calendar_id の参加者かどうか(憲章 原則III: 所有者確認はクエリ条件)。

    posts.py / events.py / calendars.py の全ての「カレンダー参加者本人のみ」判定で共通利用する。
    """
    return (
        CalendarMember.query.filter_by(calendar_id=calendar_id, user_id=user_id).first()
        is not None
    )
