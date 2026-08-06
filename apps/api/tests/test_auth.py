from .conftest import create_user


def test_register_success(client):
    resp = client.post(
        "/api/register",
        json={
            "email": "register-success@example.com",
            "password": "correct-horse",
            "display_name": "山田太郎",
        },
    )

    assert resp.status_code == 201
    body = resp.get_json()
    assert body["email"] == "register-success@example.com"
    assert body["display_name"] == "山田太郎"
    assert "password_hash" not in body
    assert "password" not in body


def test_register_duplicate_email_is_rejected(client):
    create_user("duplicate@example.com")

    resp = client.post(
        "/api/register",
        json={
            "email": "duplicate@example.com",
            "password": "another-pass",
            "display_name": "別名",
        },
    )

    assert resp.status_code == 400
    assert resp.get_json()["error"]["code"] == "invalid_request"


def test_login_success_and_me(client):
    create_user("login-success@example.com", password="correct-horse", display_name="山田太郎")

    login_resp = client.post(
        "/api/login",
        json={"email": "login-success@example.com", "password": "correct-horse"},
    )
    assert login_resp.status_code == 200
    assert "Set-Cookie" in login_resp.headers

    me_resp = client.get("/api/me")
    assert me_resp.status_code == 200
    body = me_resp.get_json()
    assert body["email"] == "login-success@example.com"
    assert body["display_name"] == "山田太郎"


def test_login_failure_is_uniform_for_missing_email_and_wrong_password(client):
    create_user("known@example.com", password="correct-horse")

    resp_missing_email = client.post(
        "/api/login",
        json={"email": "nobody@example.com", "password": "whatever"},
    )
    resp_wrong_password = client.post(
        "/api/login",
        json={"email": "known@example.com", "password": "wrong-password"},
    )

    assert resp_missing_email.status_code == 401
    assert resp_wrong_password.status_code == 401
    assert resp_missing_email.get_json() == resp_wrong_password.get_json()


def test_logout_then_me_is_unauthorized(client):
    create_user("logout-flow@example.com", password="correct-horse")
    client.post("/api/login", json={"email": "logout-flow@example.com", "password": "correct-horse"})

    logout_resp = client.post("/api/logout")
    assert logout_resp.status_code == 204

    me_resp = client.get("/api/me")
    assert me_resp.status_code == 401
    assert me_resp.get_json()["error"]["code"] == "unauthorized"
