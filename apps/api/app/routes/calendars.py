import secrets

from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required
from marshmallow import ValidationError
from sqlalchemy import func

from ..extensions import db
from ..models.calendar import Calendar, CalendarMember
from ..models.score import PointEvent
from ..models.user import User
from ..schemas.calendar import calendar_create_schema, calendar_join_schema, calendar_schema
from .utils import error_response, is_calendar_member

calendars_bp = Blueprint("calendars", __name__, url_prefix="/api")


def _generate_invite_code():
    """推測されにくいランダムな招待コードを発行する(research.md §1)。

    Calendar.invite_code は UNIQUE 制約付きのため、衝突時のみ再試行する。
    """
    for _ in range(10):
        code = secrets.token_urlsafe(6)
        if Calendar.query.filter_by(invite_code=code).first() is None:
            return code
    raise RuntimeError("招待コードの生成に失敗しました。")


@calendars_bp.post("/calendars")
@login_required
def create_group_calendar():
    """
    ---
    post:
      summary: グループカレンダーを作成する。作成者は自動的にownerとして参加する
      security:
        - cookieAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema: CalendarCreateSchema
      responses:
        201:
          description: 作成成功(招待コードを含む)
          content:
            application/json:
              schema: CalendarSchema
        400:
          description: 入力エラー
        401:
          description: 未ログイン
    """
    payload = request.get_json(silent=True) or {}
    try:
        data = calendar_create_schema.load(payload)
    except ValidationError as err:
        return error_response("validation_error", "入力内容を確認してください。", err.messages)

    calendar = Calendar(
        name=data["name"],
        type="group",
        owner_id=current_user.id,
        invite_code=_generate_invite_code(),
    )
    db.session.add(calendar)
    db.session.flush()  # CalendarMember作成前にcalendar.idを確定させる
    db.session.add(
        CalendarMember(calendar_id=calendar.id, user_id=current_user.id, role="owner")
    )
    db.session.commit()

    return jsonify(calendar_schema.dump(calendar)), 201


@calendars_bp.post("/calendars/join")
@login_required
def join_group_calendar():
    """
    ---
    post:
      summary: 招待コードでグループカレンダーに参加する。参加済みなら200(冪等)
      security:
        - cookieAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema: CalendarJoinSchema
      responses:
        201:
          description: 新規に参加した
          content:
            application/json:
              schema: CalendarSchema
        200:
          description: 既に参加済み
          content:
            application/json:
              schema: CalendarSchema
        400:
          description: 入力エラー
        401:
          description: 未ログイン
        404:
          description: 招待コードが見つからない
    """
    payload = request.get_json(silent=True) or {}
    try:
        data = calendar_join_schema.load(payload)
    except ValidationError as err:
        return error_response("validation_error", "入力内容を確認してください。", err.messages)

    calendar = Calendar.query.filter_by(invite_code=data["invite_code"], type="group").first()
    if calendar is None:
        return error_response("not_found", "招待コードが見つかりません。", status=404)

    existing = CalendarMember.query.filter_by(
        calendar_id=calendar.id, user_id=current_user.id
    ).first()
    if existing is not None:
        return jsonify(calendar_schema.dump(calendar)), 200

    db.session.add(
        CalendarMember(calendar_id=calendar.id, user_id=current_user.id, role="member")
    )
    db.session.commit()

    return jsonify(calendar_schema.dump(calendar)), 201


@calendars_bp.get("/calendars/mine")
@login_required
def get_my_personal_calendar():
    """
    自分の個人カレンダー(type=personal)を取得する。存在しない場合はここで作成する
    (get-or-create)。個人カレンダーの作成・参加を行う専用エンドポイントが無いため、
    timelineのpersonal scopeが最初にアクセスした時点で暗黙に用意する。
    ---
    get:
      summary: 自分の個人カレンダーを取得する。無ければ作成する
      security:
        - cookieAuth: []
      responses:
        200:
          description: 正常
          content:
            application/json:
              schema: CalendarSchema
        401:
          description: 未ログイン
    """
    calendar = Calendar.query.filter_by(owner_id=current_user.id, type="personal").first()
    if calendar is None:
        calendar = Calendar(
            name=f"{current_user.display_name}の個人カレンダー",
            type="personal",
            owner_id=current_user.id,
        )
        db.session.add(calendar)
        db.session.flush()  # CalendarMember作成前にcalendar.idを確定させる
        db.session.add(
            CalendarMember(calendar_id=calendar.id, user_id=current_user.id, role="owner")
        )
        db.session.commit()

    return jsonify(calendar_schema.dump(calendar)), 200


@calendars_bp.get("/calendars/<int:calendar_id>")
@login_required
def get_calendar(calendar_id):
    """
    ---
    get:
      summary: カレンダー基本情報を取得する。参加者本人のみ
      security:
        - cookieAuth: []
      responses:
        200:
          description: 正常
          content:
            application/json:
              schema: CalendarSchema
        401:
          description: 未ログイン
        404:
          description: 存在しない、または参加していないカレンダー
    """
    # 参加者本人であることの確認を先に行う(存在有無を漏らさない、憲章 原則III)。
    if not is_calendar_member(calendar_id, current_user.id):
        return error_response("not_found", "カレンダーが見つかりません。", status=404)

    calendar = Calendar.query.get(calendar_id)
    return jsonify(calendar_schema.dump(calendar)), 200


@calendars_bp.get("/calendars/<int:calendar_id>/members")
@login_required
def list_calendar_members(calendar_id):
    """
    GET /api/calendars/<id>/members?sort=score

    point_events はユーザー単位(calendar 単位ではない)のため、このカレンダーの
    メンバーそれぞれについて全期間の合計ポイントを集計してランキングする。
    集計方法・期間・並び順の正式仕様は design.md §7 の「未決事項」であり、暫定実装。
    参加者(CalendarMember)本人以外には見せない(spec.md 010-secure-social-api)。
    ---
    get:
      summary: カレンダー参加者一覧(スコアランキング)を取得する。参加者本人のみ
      security:
        - cookieAuth: []
      responses:
        200:
          description: 正常
        401:
          description: 未ログイン
        404:
          description: 存在しない、または参加していないカレンダー
    """
    if not is_calendar_member(calendar_id, current_user.id):
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
