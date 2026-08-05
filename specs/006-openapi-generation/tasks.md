---

description: "Task list template for feature implementation"
---

# Tasks: openapi.jsonの生成

**Input**: Design documents from `/specs/006-openapi-generation/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md(すべて生成済み)

**Tests**: 生成結果の構造確認テストを1本追加する(spec.mdで明示的に要求)。

**Organization**: spec.mdのUser Story(P1〜P2)ごとにグルーピングする。

## Format: `[ID] [P?] [Story] Description`

- **[P]**: 並行実行可能(別ファイル・依存なし)
- **[Story]**: US1=契約を生成物として得る, US2=実装との食い違いに気づける

---

## Phase 1: Setup

**Purpose**: 依存ライブラリの追加と反映

- [X] T001 [P] `apps/api/requirements.txt`に`apispec`, `apispec-webframeworks`をバージョン固定で追加する(憲章 原則V)
- [X] T002 依存を反映する: devコンテナ内で`pip install --user -r apps/api/requirements.txt`(T001に依存)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: スキーマ登録の土台(生成スクリプトの骨格)

**⚠️ CRITICAL**: このフェーズ完了までエンドポイントごとのdocstring追記を進めても生成できない

- [X] T003 `apps/api/generate_openapi.py`を新規作成する。`APISpec`(title, version, openapi_version="3.0.3", plugins=[FlaskPlugin(), MarshmallowPlugin()])を初期化し、`create_app()`のFlaskインスタンスを`app.test_request_context()`で使えるようにする(T002に依存)
- [X] T004 `generate_openapi.py`に、`RegisterSchema` / `LoginSchema` / `UserSchema` / `TodoSchema`を`spec.components.schema(...)`で登録する処理を追加する(T003に依存)
- [X] T005 `generate_openapi.py`に、リポジトリルート直下の`openapi.json`へ`json.dump(spec.to_dict(), ..., indent=2, ensure_ascii=False)`で書き出す処理を追加する(T004に依存)

**Checkpoint**: ここまで完了すればView関数のdocstring追記を開始できる

---

## Phase 3: User Story 1 - 開発者としてAPIの契約を生成物として得る (Priority: P1) 🎯 MVP

**Goal**: 実装済みの全エンドポイントを`openapi.json`に反映する

**Independent Test**: `python generate_openapi.py`を実行し、`openapi.json`に全エンドポイントが含まれることを確認する

### Implementation for User Story 1

- [X] T006 [P] [US1] `apps/api/app/routes/health.py`の`health()`にOpenAPI用docstring(YAML)を追記する(FR-001, FR-005: 認証不要・200レスポンス)(T005に依存)
- [X] T007 [P] [US1] `apps/api/app/routes/hello.py`の`hello()`にOpenAPI用docstringを追記する(T005に依存)
- [X] T008 [P] [US1] `apps/api/app/routes/auth.py`の`register()`/`login()`/`logout()`/`me()`にOpenAPI用docstringを追記する(FR-002, FR-005: register/loginは`RegisterSchema`/`LoginSchema`を`$ref`、レスポンスは`UserSchema`。logout/meは`@login_required`のため401レスポンスも記載)(T005に依存)
- [X] T009 [P] [US1] `apps/api/app/routes/todos.py`の`list_todos()`/`get_todo()`/`create_todo()`/`update_todo()`/`delete_todo()`にOpenAPI用docstringを追記する(FR-002, FR-005: `TodoSchema`を`$ref`、404/401レスポンスも記載)(T005に依存)
- [X] T010 [US1] `generate_openapi.py`に、T006〜T009で対象にした全View関数を`spec.path(view=...)`で登録する処理を追加する(T006, T007, T008, T009に依存)
- [X] T011 [US1] `python generate_openapi.py`を実行し、リポジトリルート直下に`openapi.json`が生成されることを確認する(T010に依存)

**Checkpoint**: 実装済み全エンドポイントの契約が生成物として得られる

---

## Phase 4: User Story 2 - 開発者として実装との食い違いに気づける (Priority: P2)

**Goal**: 生成結果を自動テストで検証し、再実行可能性を保証する

**Independent Test**: `apps/api/tests/test_openapi_generation.py`のみを実行し、全テストがパスすることを確認する

### Implementation for User Story 2

- [X] T012 [US2] `apps/api/tests/test_openapi_generation.py`に、生成された`openapi.json`の`paths`に対象8エンドポイント(`/api/health`, `/api/hello`, `/api/register`, `/api/login`, `/api/logout`, `/api/me`, `/api/todos`, `/api/todos/{todo_id}`)がすべて含まれることを検証するテストを実装する(SC-001)(T011に依存)
- [X] T013 [US2] `apps/api/tests/test_openapi_generation.py`に、生成を2回連続で実行して`openapi.json`の内容が一致すること(FR-006: 再実行可能性)を検証するテストを実装する(T012に依存)

**Checkpoint**: 生成結果が自動テストで保証される

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: ドキュメント整合と最終確認

- [X] T014 [P] `apps/api/README.md`に「openapi.jsonの生成方法」節を追加する(quickstart.mdの手順を要約して転記)
- [X] T015 `apps/api`ディレクトリで`python -m pytest`を実行し、`005-api-tests`の既存テストを含め全テストがパスすることを確認する(既存テストへの回帰がないことの確認)(T013に依存)
- [X] T016 `quickstart.md`の全手順を通しで再実行し、最終確認する(T011〜T015に依存)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: 依存なし。即着手可
- **Foundational (Phase 2)**: Setup完了後。**User Story 1をブロックする**
- **User Story 1 (Phase 3)**: Foundational完了後
- **User Story 2 (Phase 4)**: User Story 1完了後(生成結果が無いとテストできないため)
- **Polish (Phase 5)**: 全User Story完了後

### User Story Dependencies

- **US1(契約の生成, P1)**: Foundational完了後に開始可。他Storyに依存しない
- **US2(食い違いの検知, P2)**: US1の生成結果に依存する(US1が無いとテスト対象が存在しない)

### Parallel Opportunities

- Setup: T001は単独タスク
- User Story 1: T006, T007, T008, T009は別ファイルのため並行実行可能
- Polish: T014は他タスクと並行可能

---

## Parallel Example: User Story 1

```bash
# T005完了後、以下は並行実行可能
Task: "apps/api/app/routes/health.py にOpenAPI用docstringを追記"
Task: "apps/api/app/routes/hello.py にOpenAPI用docstringを追記"
Task: "apps/api/app/routes/auth.py にOpenAPI用docstringを追記"
Task: "apps/api/app/routes/todos.py にOpenAPI用docstringを追記"
```

---

## Implementation Strategy

### MVP First (User Story 1)

1. Phase 1: Setup
2. Phase 2: Foundational(**必須**)
3. Phase 3: US1(契約の生成)— ここまでで`openapi.json`が実際に生成される
4. **STOP and VALIDATE**: `python generate_openapi.py`の実行結果を確認

### Incremental Delivery

1. Setup + Foundational → 基盤完成
2. US1(契約の生成)→ 独立検証(MVP到達)
3. US2(食い違いの検知)→ 独立検証
4. Polish(ドキュメント整合・全体の最終確認)

---

## Notes

- 各タスク完了後にコミットすることを推奨する。
- チェックポイントごとに独立して動作確認できる。
