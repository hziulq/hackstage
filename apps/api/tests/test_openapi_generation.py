import json

from generate_openapi import OUTPUT_PATH, build_spec

EXPECTED_PATHS = {
    "/api/health",
    "/api/hello",
    "/api/register",
    "/api/login",
    "/api/logout",
    "/api/me",
    "/api/todos",
    "/api/todos/{todo_id}",
    # 010-secure-social-api: 認証統合済みの新規エンドポイント。
    "/api/posts",
    "/api/posts/{post_id}/comments",
    "/api/goals",
    "/api/goals/{goal_id}",
    "/api/goals/{goal_id}/milestones/{milestone_id}",
    "/api/events",
    "/api/reactions",
    "/api/reactions/{reaction_id}",
    "/api/calendars/mine",
    "/api/calendars/{calendar_id}",
    "/api/calendars/{calendar_id}/members",
}


def test_generated_spec_contains_all_implemented_endpoints():
    spec = build_spec().to_dict()

    assert set(spec["paths"].keys()) == EXPECTED_PATHS


def test_generation_is_reproducible():
    first = build_spec().to_dict()
    second = build_spec().to_dict()

    assert first == second


def test_openapi_json_file_matches_current_build():
    with open(OUTPUT_PATH, encoding="utf-8") as f:
        on_disk = json.load(f)

    assert on_disk["paths"].keys() == build_spec().to_dict()["paths"].keys()
