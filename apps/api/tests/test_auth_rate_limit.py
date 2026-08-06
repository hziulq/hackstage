from .conftest import create_user


def test_login_is_rate_limited_after_five_attempts_per_minute(client):
    create_user("rate-limit@example.com", password="correct-horse")

    statuses = []
    for _ in range(6):
        resp = client.post(
            "/api/login",
            json={"email": "rate-limit@example.com", "password": "wrong-password"},
        )
        statuses.append(resp.status_code)

    assert statuses[:5] == [401, 401, 401, 401, 401]
    assert statuses[5] == 429
