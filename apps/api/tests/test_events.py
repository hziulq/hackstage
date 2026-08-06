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
