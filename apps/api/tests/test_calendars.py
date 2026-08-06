from app.extensions import db as _db
from app.models.calendar import Calendar, CalendarMember

from .conftest import create_user


def _login(client, email, password="correct-horse"):
    resp = client.post("/api/login", json={"email": email, "password": password})
    assert resp.status_code == 200


def _create_calendar_with_members(owner_id, member_ids):
    calendar = Calendar(name="グループ", type="group", owner_id=owner_id)
    _db.session.add(calendar)
    _db.session.flush()
    for uid in member_ids:
        _db.session.add(CalendarMember(calendar_id=calendar.id, user_id=uid))
    _db.session.commit()
    return calendar


def test_calendar_requires_login(client):
    resp = client.get("/api/calendars/1")
    assert resp.status_code == 401
    resp = client.get("/api/calendars/1/members")
    assert resp.status_code == 401


def test_calendar_non_member_gets_404(client):
    owner = create_user("calendar-owner@example.com")
    create_user("calendar-outsider@example.com")
    calendar = _create_calendar_with_members(owner.id, [owner.id])

    _login(client, "calendar-outsider@example.com")
    resp = client.get(f"/api/calendars/{calendar.id}")
    assert resp.status_code == 404
    resp = client.get(f"/api/calendars/{calendar.id}/members")
    assert resp.status_code == 404


def test_calendar_member_can_view(client):
    owner = create_user("calendar-owner2@example.com")
    member = create_user("calendar-member2@example.com")
    calendar = _create_calendar_with_members(owner.id, [owner.id, member.id])

    _login(client, "calendar-member2@example.com")
    resp = client.get(f"/api/calendars/{calendar.id}")
    assert resp.status_code == 200
    assert resp.get_json()["id"] == calendar.id

    resp = client.get(f"/api/calendars/{calendar.id}/members")
    assert resp.status_code == 200
    user_ids = {m["user_id"] for m in resp.get_json()}
    assert user_ids == {owner.id, member.id}


def test_mine_requires_login(client):
    resp = client.get("/api/calendars/mine")
    assert resp.status_code == 401


def test_mine_creates_personal_calendar_once(client):
    owner = create_user("mine-owner@example.com")
    _login(client, "mine-owner@example.com")

    first = client.get("/api/calendars/mine")
    assert first.status_code == 200
    body = first.get_json()
    assert body["type"] == "personal"
    assert body["owner_id"] == owner.id

    member = CalendarMember.query.filter_by(calendar_id=body["id"], user_id=owner.id).first()
    assert member is not None

    second = client.get("/api/calendars/mine")
    assert second.status_code == 200
    assert second.get_json()["id"] == body["id"]  # 2回目は新規作成しない

    assert Calendar.query.filter_by(owner_id=owner.id, type="personal").count() == 1


def test_create_group_calendar_requires_login(client):
    resp = client.post("/api/calendars", json={"name": "テストグループ"})
    assert resp.status_code == 401


def test_create_group_calendar_issues_invite_code(client):
    owner = create_user("group-owner@example.com")
    _login(client, "group-owner@example.com")

    resp = client.post("/api/calendars", json={"name": "同期就活グループ"})
    assert resp.status_code == 201
    body = resp.get_json()
    assert body["type"] == "group"
    assert body["owner_id"] == owner.id
    assert body["invite_code"]

    members_resp = client.get(f"/api/calendars/{body['id']}/members")
    assert members_resp.status_code == 200
    members = members_resp.get_json()
    assert len(members) == 1
    assert members[0]["user_id"] == owner.id
    assert members[0]["role"] == "owner"


def test_join_group_calendar_with_invalid_code_gets_404(client):
    create_user("join-user@example.com")
    _login(client, "join-user@example.com")

    resp = client.post("/api/calendars/join", json={"invite_code": "does-not-exist"})
    assert resp.status_code == 404


def test_join_group_calendar_is_idempotent(client):
    create_user("join-owner@example.com")
    joiner = create_user("join-joiner@example.com")

    _login(client, "join-owner@example.com")
    create_resp = client.post("/api/calendars", json={"name": "参加テストグループ"})
    calendar = create_resp.get_json()

    client.post("/api/logout")
    _login(client, "join-joiner@example.com")

    first_join = client.post("/api/calendars/join", json={"invite_code": calendar["invite_code"]})
    assert first_join.status_code == 201

    second_join = client.post("/api/calendars/join", json={"invite_code": calendar["invite_code"]})
    assert second_join.status_code == 200  # 重複参加はエラーにならない(冪等)

    members_resp = client.get(f"/api/calendars/{calendar['id']}/members")
    user_ids = [m["user_id"] for m in members_resp.get_json()]
    assert user_ids.count(joiner.id) == 1  # 二重登録されていない
