from app.models.goal import GoalMilestone

from .conftest import create_user


def _login(client, email, password="correct-horse"):
    resp = client.post("/api/login", json={"email": email, "password": password})
    assert resp.status_code == 200


def test_goals_requires_login(client):
    list_resp = client.get("/api/goals")
    create_resp = client.post(
        "/api/goals",
        json={"company_name": "テスト株式会社", "stage": "ES", "target_date": "2026-12-01"},
    )
    assert list_resp.status_code == 401
    assert create_resp.status_code == 401


def test_goals_are_isolated_per_owner(client):
    create_user("goal-owner-a@example.com")
    create_user("goal-owner-b@example.com")

    _login(client, "goal-owner-a@example.com")
    # user_id はサーバー側で current_user.id から補うため、クライアント指定は
    # 「不一致として拒否」される(spec.md Acceptance Scenario 2、dump_onlyフィールド)。
    rejected_resp = client.post(
        "/api/goals",
        json={
            "user_id": 9999,
            "company_name": "A社",
            "stage": "ES",
            "target_date": "2026-12-01",
            "milestones": [],
        },
    )
    assert rejected_resp.status_code == 400

    create_resp = client.post(
        "/api/goals",
        json={
            "company_name": "A社",
            "stage": "ES",
            "target_date": "2026-12-01",
            "milestones": [],
        },
    )
    assert create_resp.status_code == 201
    goal = create_resp.get_json()
    assert goal["user_id"] != 9999

    client.post("/api/logout")
    _login(client, "goal-owner-b@example.com")

    list_resp = client.get("/api/goals")
    assert list_resp.status_code == 200
    assert list_resp.get_json() == []

    delete_resp = client.delete(f"/api/goals/{goal['id']}")
    assert delete_resp.status_code == 404


def test_goal_response_includes_nested_milestones(client):
    create_user("goal-milestones@example.com")
    _login(client, "goal-milestones@example.com")

    create_resp = client.post(
        "/api/goals",
        json={
            "company_name": "C社",
            "stage": "ES",
            "target_date": "2026-12-01",
            "milestones": [
                {"title": "ES提出", "offset_days": -30},
                {"title": "一次面接", "offset_days": -14},
            ],
        },
    )
    assert create_resp.status_code == 201
    goal = create_resp.get_json()
    assert [m["title"] for m in goal["milestones"]] == ["ES提出", "一次面接"]
    assert all(m["done"] is False for m in goal["milestones"])

    list_resp = client.get("/api/goals")
    assert list_resp.status_code == 200
    listed_goal = list_resp.get_json()[0]
    assert len(listed_goal["milestones"]) == 2


def test_milestone_toggle_requires_ownership(client):
    create_user("milestone-owner@example.com")
    create_user("milestone-other@example.com")

    _login(client, "milestone-owner@example.com")
    create_resp = client.post(
        "/api/goals",
        json={
            "company_name": "B社",
            "stage": "ES",
            "target_date": "2026-12-01",
            "milestones": [{"title": "ES提出", "offset_days": -30}],
        },
    )
    goal = create_resp.get_json()
    milestone = GoalMilestone.query.filter_by(goal_id=goal["id"]).first()

    client.post("/api/logout")
    _login(client, "milestone-other@example.com")
    resp = client.patch(
        f"/api/goals/{goal['id']}/milestones/{milestone.id}", json={"done": True}
    )
    assert resp.status_code == 404

    client.post("/api/logout")
    _login(client, "milestone-owner@example.com")
    resp = client.patch(
        f"/api/goals/{goal['id']}/milestones/{milestone.id}", json={"done": True}
    )
    assert resp.status_code == 200
    assert resp.get_json()["done"] is True
