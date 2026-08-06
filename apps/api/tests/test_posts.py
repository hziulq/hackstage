from app.extensions import db as _db
from app.models.calendar import Calendar, CalendarMember
from app.models.board import Post

from .conftest import create_user


def _login(client, email, password="correct-horse"):
    resp = client.post("/api/login", json={"email": email, "password": password})
    assert resp.status_code == 200


def _create_calendar(owner_id, type_="personal"):
    calendar = Calendar(name="テストカレンダー", type=type_, owner_id=owner_id)
    _db.session.add(calendar)
    _db.session.flush()
    _db.session.add(CalendarMember(calendar_id=calendar.id, user_id=owner_id))
    _db.session.commit()
    return calendar


def test_posts_requires_login(client):
    list_resp = client.get("/api/posts", query_string={"category": "anonymous_qa"})
    create_resp = client.post(
        "/api/posts", json={"category": "anonymous_qa", "body": "質問です"}
    )
    comment_resp = client.post("/api/posts/1/comments", json={"body": "回答です"})

    assert list_resp.status_code == 401
    assert create_resp.status_code == 401
    assert comment_resp.status_code == 401


def test_create_post_uses_current_user(client):
    owner = create_user("post-owner@example.com")
    _login(client, "post-owner@example.com")

    resp = client.post(
        "/api/posts",
        json={"category": "prefecture_intern_info", "body": "自分の投稿"},
    )
    assert resp.status_code == 201
    assert resp.get_json()["user_id"] == owner.id

    post = Post.query.get(resp.get_json()["id"])
    assert post.user_id == owner.id


def test_create_post_rejects_client_supplied_user_id(client):
    owner = create_user("post-owner2@example.com")
    other = create_user("post-other2@example.com")
    _login(client, "post-owner2@example.com")

    # user_id はサーバー側で current_user.id から補うため、クライアント指定は
    # 「不一致として拒否」される(spec.md Acceptance Scenario 2、dump_onlyフィールド)。
    resp = client.post(
        "/api/posts",
        json={"user_id": other.id, "category": "prefecture_intern_info", "body": "なりすまし"},
    )
    assert resp.status_code == 400


def test_posts_calendar_scope_requires_membership(client):
    owner = create_user("cal-owner@example.com")
    create_user("cal-outsider@example.com")
    calendar = _create_calendar(owner.id, type_="personal")

    _login(client, "cal-outsider@example.com")
    resp = client.get("/api/posts", query_string={"calendar_id": calendar.id})
    assert resp.status_code == 404

    resp = client.post(
        "/api/posts",
        json={
            "category": "timeline",
            "body": "他人の個人カレンダーに投稿しようとする",
            "calendar_id": calendar.id,
        },
    )
    assert resp.status_code == 404

    client.post("/api/logout")
    _login(client, "cal-owner@example.com")
    resp = client.get("/api/posts", query_string={"calendar_id": calendar.id})
    assert resp.status_code == 200
