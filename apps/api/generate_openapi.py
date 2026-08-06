"""実装済みエンドポイントからopenapi.jsonを生成する(006-openapi-generation)。

DB接続は不要(View関数を実際には呼び出さず、ルーティング情報とdocstringのみを読む)。
実行方法・詳細は specs/006-openapi-generation/quickstart.md を参照。
"""

import json
import os

from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec_webframeworks.flask import FlaskPlugin
from app import create_app
from app.schemas.calendar import CalendarCreateSchema, CalendarJoinSchema, CalendarSchema
from app.schemas.event import EventSchema
from app.schemas.goal import GoalCreateSchema, GoalMilestonePatchSchema, GoalSchema
from app.schemas.post import PostCommentSchema, PostSchema
from app.schemas.reaction import ReactionSchema
from app.schemas.todo import TodoSchema
from app.schemas.user import LoginSchema, RegisterSchema, UserSchema

_APPS_API_DIR = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.dirname(os.path.dirname(_APPS_API_DIR))
OUTPUT_PATH = os.path.join(_REPO_ROOT, "openapi.json")


def build_spec():
    spec = APISpec(
        title="hackstage api",
        version="1.0.0",
        openapi_version="3.0.3",
        info={"description": "docs/design.md §7 の契約から生成"},
        plugins=[FlaskPlugin(), MarshmallowPlugin()],
    )

    spec.components.security_scheme(
        "cookieAuth",
        {"type": "apiKey", "in": "cookie", "name": "session"},
    )

    # スキーマ登録は既存のmarshmallow Schemaをそのまま使う(FR-002)。
    spec.components.schema("Register", schema=RegisterSchema)
    spec.components.schema("Login", schema=LoginSchema)
    spec.components.schema("User", schema=UserSchema)
    spec.components.schema("Todo", schema=TodoSchema)
    # 010-secure-social-api: 認証統合済みの posts/goals/events/reactions/calendars を追加。
    spec.components.schema("Post", schema=PostSchema)
    spec.components.schema("PostComment", schema=PostCommentSchema)
    # GoalMilestoneはGoalSchemaのNestedフィールドから自動登録されるため明示登録しない
    # (DuplicateComponentNameErrorになる)。
    spec.components.schema("Goal", schema=GoalSchema)
    spec.components.schema("GoalCreate", schema=GoalCreateSchema)
    spec.components.schema("GoalMilestonePatch", schema=GoalMilestonePatchSchema)
    spec.components.schema("Event", schema=EventSchema)
    spec.components.schema("Reaction", schema=ReactionSchema)
    spec.components.schema("Calendar", schema=CalendarSchema)
    # 011-events-calendar-sharing: グループカレンダー作成・招待コード参加を追加。
    spec.components.schema("CalendarCreate", schema=CalendarCreateSchema)
    spec.components.schema("CalendarJoin", schema=CalendarJoinSchema)

    app = create_app()

    # 対象は実装済みエンドポイントのみ(research.md §6)。
    view_functions = [
        app.view_functions["health.health"],
        app.view_functions["hello.hello"],
        app.view_functions["auth.register"],
        app.view_functions["auth.login"],
        app.view_functions["auth.logout"],
        app.view_functions["auth.me"],
        app.view_functions["todos.list_todos"],
        app.view_functions["todos.get_todo"],
        app.view_functions["todos.create_todo"],
        app.view_functions["todos.update_todo"],
        app.view_functions["todos.delete_todo"],
        # 010-secure-social-api: 認証統合済みの新規エンドポイント。
        app.view_functions["posts.list_posts"],
        app.view_functions["posts.create_post"],
        app.view_functions["posts.list_post_comments"],
        app.view_functions["posts.create_post_comment"],
        app.view_functions["goals.list_goals"],
        app.view_functions["goals.create_goal"],
        app.view_functions["goals.update_milestone"],
        app.view_functions["goals.delete_goal"],
        app.view_functions["events.list_events"],
        app.view_functions["events.create_event"],
        app.view_functions["reactions.list_reactions"],
        app.view_functions["reactions.create_reaction"],
        app.view_functions["reactions.delete_reaction"],
        app.view_functions["calendars.get_my_personal_calendar"],
        app.view_functions["calendars.get_calendar"],
        app.view_functions["calendars.list_calendar_members"],
        # 011-events-calendar-sharing: グループカレンダー作成・招待コード参加。
        app.view_functions["calendars.create_group_calendar"],
        app.view_functions["calendars.join_group_calendar"],
    ]

    with app.test_request_context():
        for view in view_functions:
            spec.path(view=view)

    return spec


def main():
    spec = build_spec()
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(spec.to_dict(), f, indent=2, ensure_ascii=False, sort_keys=False)
        f.write("\n")
    print(f"wrote {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
