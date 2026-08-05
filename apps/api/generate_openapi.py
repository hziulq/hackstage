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
