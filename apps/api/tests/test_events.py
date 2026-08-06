from datetime import datetime, timezone

from app.extensions import db as _db
from app.models.calendar import Calendar, CalendarMember
from app.models.event import Event

from .conftest import create_user


def _login(client, email, password="correct-horse"):
    resp = client.post("/api/login", json={"email": email, "password": password})
    assert resp.status_code == 200


def _create_calendar_with_members(owner_id, member_ids):
    calendar = Calendar(name="部活", type="group", owner_id=owner_id)
    _db.session.add(calendar)
    _db.session.flush()
    for uid in member_ids:
        _db.session.add(CalendarMember(calendar_id=calendar.id, user_id=uid))
    _db.session.commit()
    return calendar


def test_events_requires_login(client):
    resp = client.get("/api/events", query_string={"calendar_id": 1})
    assert resp.status_code == 401
    resp = client.post(
        "/api/events",
        json={
            "calendar_id": 1,
            "category": "interview",
            "title": "無視されるはず",
            "start_at": "2026-09-01T10:00:00+09:00",
        },
    )
    assert resp.status_code == 401


def test_create_event_requires_calendar_membership(client):
    owner = create_user("create-event-owner@example.com")
    create_user("create-event-outsider@example.com")
    calendar = _create_calendar_with_members(owner.id, [owner.id])

    _login(client, "create-event-outsider@example.com")
    resp = client.post(
        "/api/events",
        json={
            "calendar_id": calendar.id,
            "category": "interview",
            "title": "侵入テスト",
            "start_at": "2026-09-01T10:00:00+09:00",
        },
    )
    assert resp.status_code == 404


def test_create_event_uses_current_user_and_respects_is_private(client):
    owner = create_user("create-event-a@example.com")
    other = create_user("create-event-b@example.com")
    calendar = _create_calendar_with_members(owner.id, [owner.id, other.id])

    _login(client, "create-event-a@example.com")
    public_resp = client.post(
        "/api/events",
        json={
            "calendar_id": calendar.id,
            "category": "es",
            "title": "公開の予定",
            "start_at": "2026-09-01T10:00:00+09:00",
        },
    )
    assert public_resp.status_code == 201
    assert public_resp.get_json()["user_id"] == owner.id

    private_resp = client.post(
        "/api/events",
        json={
            "calendar_id": calendar.id,
            "category": "other",
            "title": "非公開の予定",
            "start_at": "2026-09-02T10:00:00+09:00",
            "is_private": True,
        },
    )
    assert private_resp.status_code == 201

    client.post("/api/logout")
    _login(client, "create-event-b@example.com")
    list_resp = client.get("/api/events", query_string={"calendar_id": calendar.id})
    titles = [e["title"] for e in list_resp.get_json()]
    assert titles == ["公開の予定"]


def test_events_requires_calendar_membership(client):
    owner = create_user("event-owner@example.com")
    create_user("event-outsider@example.com")
    calendar = _create_calendar_with_members(owner.id, [owner.id])

    _login(client, "event-outsider@example.com")
    resp = client.get("/api/events", query_string={"calendar_id": calendar.id})
    assert resp.status_code == 404


def test_private_events_hidden_from_other_members(client):
    owner = create_user("private-owner@example.com")
    member = create_user("private-member@example.com")
    calendar = _create_calendar_with_members(owner.id, [owner.id, member.id])

    now = datetime(2026, 1, 1, tzinfo=timezone.utc)
    _db.session.add(
        Event(
            calendar_id=calendar.id,
            user_id=owner.id,
            category="interview",
            title="非公開の面接",
            start_at=now,
            is_private=True,
        )
    )
    _db.session.add(
        Event(
            calendar_id=calendar.id,
            user_id=owner.id,
            category="es",
            title="公開のES提出",
            start_at=now,
            is_private=False,
        )
    )
    _db.session.commit()

    _login(client, "private-member@example.com")
    resp = client.get("/api/events", query_string={"calendar_id": calendar.id})
    assert resp.status_code == 200
    titles = [e["title"] for e in resp.get_json()]
    assert titles == ["公開のES提出"]

    client.post("/api/logout")
    _login(client, "private-owner@example.com")
    resp = client.get("/api/events", query_string={"calendar_id": calendar.id})
    titles = sorted(e["title"] for e in resp.get_json())
    assert titles == ["公開のES提出", "非公開の面接"]
