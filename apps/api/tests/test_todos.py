from .conftest import create_user


def _login(client, email, password="correct-horse"):
    resp = client.post("/api/login", json={"email": email, "password": password})
    assert resp.status_code == 200


def test_todos_requires_login(client):
    list_resp = client.get("/api/todos")
    create_resp = client.post("/api/todos", json={"title": "無視されるはず"})

    assert list_resp.status_code == 401
    assert create_resp.status_code == 401


def test_todos_are_isolated_per_owner(client):
    create_user("owner-a@example.com")
    create_user("owner-b@example.com")

    _login(client, "owner-a@example.com")
    create_resp = client.post("/api/todos", json={"title": "Aのtodo"})
    assert create_resp.status_code == 201
    todo_id = create_resp.get_json()["id"]
    client.post("/api/logout")

    _login(client, "owner-b@example.com")
    list_resp = client.get("/api/todos")
    assert list_resp.status_code == 200
    assert list_resp.get_json() == []

    get_resp = client.get(f"/api/todos/{todo_id}")
    assert get_resp.status_code == 404


def test_owner_can_crud_own_todo(client):
    create_user("crud-owner@example.com")
    _login(client, "crud-owner@example.com")

    create_resp = client.post("/api/todos", json={"title": "買い物"})
    assert create_resp.status_code == 201
    todo = create_resp.get_json()
    todo_id = todo["id"]

    list_resp = client.get("/api/todos")
    assert list_resp.status_code == 200
    assert [t["id"] for t in list_resp.get_json()] == [todo_id]

    update_resp = client.put(f"/api/todos/{todo_id}", json={"is_done": True})
    assert update_resp.status_code == 200
    assert update_resp.get_json()["is_done"] is True

    delete_resp = client.delete(f"/api/todos/{todo_id}")
    assert delete_resp.status_code == 204

    get_resp = client.get(f"/api/todos/{todo_id}")
    assert get_resp.status_code == 404
