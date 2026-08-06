from app.extensions import db as _db
from app.models.board import Post

from .conftest import create_user


def _login(client, email, password="correct-horse"):
    resp = client.post("/api/login", json={"email": email, "password": password})
    assert resp.status_code == 200


def _create_post(user_id):
    post = Post(user_id=user_id, category="prefecture_intern_info", body="対象の投稿")
    _db.session.add(post)
    _db.session.commit()
    return post


def test_reactions_requires_login(client):
    resp = client.post(
        "/api/reactions", json={"target_type": "post", "target_id": 1, "kind": "fire"}
    )
    assert resp.status_code == 401
    resp = client.get("/api/reactions", query_string={"target_type": "post", "target_id": 1})
    assert resp.status_code == 401


def test_list_reactions_for_target(client):
    author = create_user("reaction-list-author@example.com")
    reactor_a = create_user("reaction-list-a@example.com")
    reactor_b = create_user("reaction-list-b@example.com")
    post = _create_post(author.id)
    other_post = _create_post(author.id)

    _login(client, "reaction-list-a@example.com")
    client.post(
        "/api/reactions",
        json={"target_type": "post", "target_id": post.id, "kind": "fire"},
    )
    client.post("/api/logout")

    _login(client, "reaction-list-b@example.com")
    client.post(
        "/api/reactions",
        json={"target_type": "post", "target_id": post.id, "kind": "fire"},
    )
    # 別対象へのリアクションは一覧に含まれないことも確認する。
    client.post(
        "/api/reactions",
        json={"target_type": "post", "target_id": other_post.id, "kind": "party"},
    )

    resp = client.get(
        "/api/reactions", query_string={"target_type": "post", "target_id": post.id}
    )
    assert resp.status_code == 200
    user_ids = {r["user_id"] for r in resp.get_json()}
    assert user_ids == {reactor_a.id, reactor_b.id}

    bad_resp = client.get(
        "/api/reactions", query_string={"target_type": "invalid", "target_id": post.id}
    )
    assert bad_resp.status_code == 400


def test_reaction_ignores_client_user_id_and_ownership_enforced(client):
    author = create_user("reaction-author@example.com")
    reactor = create_user("reaction-user@example.com")
    create_user("reaction-other@example.com")
    post = _create_post(author.id)

    _login(client, "reaction-user@example.com")

    # user_id はサーバー側で current_user.id から補うため、クライアント指定は
    # 「不一致として拒否」される(spec.md Acceptance Scenario 2、dump_onlyフィールド)。
    rejected_resp = client.post(
        "/api/reactions",
        json={
            "user_id": 9999,
            "target_type": "post",
            "target_id": post.id,
            "kind": "fire",
        },
    )
    assert rejected_resp.status_code == 400

    resp = client.post(
        "/api/reactions",
        json={"target_type": "post", "target_id": post.id, "kind": "fire"},
    )
    assert resp.status_code == 201
    reaction = resp.get_json()
    assert reaction["user_id"] == reactor.id

    client.post("/api/logout")
    _login(client, "reaction-other@example.com")
    delete_resp = client.delete(f"/api/reactions/{reaction['id']}")
    assert delete_resp.status_code == 404

    client.post("/api/logout")
    _login(client, "reaction-user@example.com")
    delete_resp = client.delete(f"/api/reactions/{reaction['id']}")
    assert delete_resp.status_code == 204
