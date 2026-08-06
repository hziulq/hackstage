---

description: "Task list template for feature implementation"
---

# Tasks: 掲示板・目標・カレンダーAPIの認証統合

**Input**: Design documents from `/specs/010-secure-social-api/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/social-api.md, quickstart.md(すべて生成済み)

**Tests**: `005-api-tests`で確立済みのpytestパターン(`tests/conftest.py`の`create_user`/`db_session`/`client`フィクスチャ)に従い、各User Storyにテストタスクを含める。

**Organization**: spec.mdのUser Story(P1〜P3)ごとにグルーピング。

## Format: `[ID] [P?] [Story] Description`

- **[P]**: 並行実行可能(別ファイル・依存なし)
- **[Story]**: US1=API認証統合, US2=Web UI統合, US3=契約反映(openapi.json/型生成)

---

## Phase 1: Setup

**Purpose**: 本feature着手の前提となるブランチ統合

- [X] T001 `origin/008-auth-todo-api`を`010-secure-social-api`にマージする(`git merge`、コンフリクトなし)— 完了。`apps/api/app/routes/{posts,goals,events,reactions,calendars}.py`等が追加された
- [X] T002 `origin/008-web-auth-openapi-types`を`010-secure-social-api`にマージする(`git merge`、コンフリクトなし)— 完了。`apps/web/src/app/{login,register}/`・`proxy.ts`・`api-types.generated.ts`等が追加された
- [X] T003 [P] `apps/api/app/__init__.py`の`todos_bp`重複import(マージ元`008-auth-todo-api`由来)を整理する — 完了
- [X] T004 [P] `apps/api/app/routes/reactions.py`冒頭の`from flask import Blueprint, jsonify, request`重複import(マージ元`008-auth-todo-api`由来、research.md §10)を整理する — 完了(T012と同時に実施)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: 全User Storyが依存する共通基盤の確認・整合

**⚠️ CRITICAL**: このフェーズ完了までUser Story実装を開始しない

- [X] T005 [P] `docs/design.md` §8「画面遷移の制御: web: `middleware.ts`」を`web: proxy.ts`に修正する(憲章 原則I、research.md §9。`008-web-auth-openapi-types`が実装した`apps/web/src/proxy.ts`はNext.js 16の命名規則に準拠しており実装側の変更は不要)

> 注記: `current_user`/`@login_required`(flask_login)自体は`003-user-auth`で確立済みでマージ済みコードにそのまま含まれているため、新規の認証基盤構築は不要。

**Checkpoint**: ここまで完了すればUser Story実装を開始できる

---

## Phase 3: User Story 1 - 開発者として掲示板・目標・カレンダーAPIをなりすまし不可能にする (Priority: P1) 🎯 MVP

**Goal**: `posts`/`goals`/`calendars`/`events`/`reactions`の全エンドポイントを`current_user`/`@login_required`ベースの認証・所有者確認に置き換える(FR-001〜FR-003)

**Independent Test**: 未ログイン状態で保護対象エンドポイントを呼ぶと401、ログイン済みの別ユーザーのIDを`user_id`として渡しても本人のデータとしてしか操作できないことを確認する

### Implementation for User Story 1

- [X] T006 [P] [US1] `apps/api/app/routes/posts.py`の`list_posts`/`create_post`/`create_post_comment`に`@login_required`を付与し、`current_user.id`で投稿・コメントを作成する。`calendar_id`が指定された場合は`CalendarMember`による参加確認を追加する(non-member/未参加は404、data-model.md参照)— 完了。共通の`is_calendar_member()`を`routes/utils.py`に追加して利用
- [X] T007 [P] [US1] `apps/api/app/schemas/post.py`の`PostSchema.user_id`/`PostCommentSchema.user_id`を`fields.Int(dump_only=True)`に変更する(research.md §4)
- [X] T008 [P] [US1] `apps/api/app/routes/goals.py`の`list_goals`/`create_goal`/`update_milestone`/`delete_goal`に`@login_required`を付与し、クエリパラメータ`user_id`を廃止して`current_user.id`をクエリ条件・作成時の値として使う(todos.pyと同じパターン)
- [X] T009 [P] [US1] `apps/api/app/schemas/goal.py`の`GoalSchema.user_id`(`GoalCreateSchema`が継承)を`fields.Int(dump_only=True)`に変更する
- [X] T010 [P] [US1] `apps/api/app/routes/events.py`の`list_events`に`@login_required`を付与し、`current_user`が`calendar_id`の`CalendarMember`であることを確認(非参加者は404)。`is_private=True`の予定は`Event.user_id == current_user.id`のものだけをクエリ条件に含める(既存の`TODO`コメントを解消、data-model.md参照)
- [X] T011 [P] [US1] `apps/api/app/schemas/event.py`の`EventSchema.user_id`を`fields.Int(dump_only=True)`に変更する
- [X] T012 [P] [US1] `apps/api/app/routes/reactions.py`の`create_reaction`/`delete_reaction`に`@login_required`を付与し、`current_user.id`をリアクション作成・所有者確認に使う(T004完了後に実施)
- [X] T013 [P] [US1] `apps/api/app/schemas/reaction.py`の`ReactionSchema.user_id`を`fields.Int(dump_only=True)`に変更する
- [X] T014 [US1] `apps/api/app/routes/calendars.py`の`get_calendar`/`list_calendar_members`に`@login_required`を付与し、`current_user`が`CalendarMember`(該当`calendar_id`)であることを確認する(非参加者・存在しないカレンダーはいずれも404、spec.md Edge Cases)

### Tests for User Story 1

- [X] T015 [P] [US1] `apps/api/tests/test_posts.py`を新規作成し、未ログイン401・`calendar_id`非メンバーの404・`user_id`指定を無視して`current_user.id`で作成されることを検証する(`tests/test_todos.py`のパターンに従う)— **実際の挙動**: `user_id`は`dump_only`のためペイロードに含めると400「Unknown field」で拒否される(spec.mdが許容する「不一致として拒否」に該当)。テストはその挙動を検証する形に調整済み
- [X] T016 [P] [US1] `apps/api/tests/test_goals.py`を新規作成し、未ログイン401・他ユーザーの目標/マイルストーンへの操作が404になることを検証する
- [X] T017 [P] [US1] `apps/api/tests/test_events.py`を新規作成し、未ログイン401・非メンバー404・他人の`is_private`予定が一覧に含まれないことを検証する
- [X] T018 [P] [US1] `apps/api/tests/test_reactions.py`を新規作成し、未ログイン401・他ユーザーのリアクション削除が404になることを検証する(T015と同じ理由でuser_id拒否の挙動も検証)
- [X] T019 [P] [US1] `apps/api/tests/test_calendars.py`を新規作成し、未ログイン401・非メンバー404・メンバー本人は200になることを検証する

- [X] T020 [US1] `quickstart.md`シナリオ1〜3を実行し、401・なりすまし拒否・カレンダー非参加者404を確認する(T006〜T019に依存)— `docker`/`curl`がこの環境から使えないため、T015〜T019のpytestスイート(27件全パス)で同内容をカバーして検証済み

**Checkpoint**: この時点でAPI側の認証統合が単独で動作・検証可能(将来`api`をRenderの公開`web`サービスへ切り替えても安全な状態になる)

---

## Phase 4: User Story 2 - 開発者としてログイン/登録のWeb UIをpreviewに統合する (Priority: P2)

**Goal**: `008-web-auth-openapi-types`のログイン/登録UI・`proxy.ts`が実際に動作することを確認する(FR-004)。コード自体はT002で既にマージ済みのため、本フェーズは整合確認が中心

**Independent Test**: ブラウザで`/register`から新規登録し、`/login`でログインし、認証必須ページ(`/timeline`等)にアクセスできること。未ログイン状態では`/login`にリダイレクトされること

### Implementation for User Story 2

- [X] T021 [US2] `apps/web/src/lib/api.ts`・`auth.ts`・`auth.server.ts`・`api.server.ts`が呼び出すパス(`/api/register`・`/api/login`・`/api/logout`・`/api/me`)が現在の`apps/api/app/routes/auth.py`の実装と一致していることを確認する。ずれがあれば`apps/web`側を修正する — 確認済み、修正不要
- [X] T022 [US2] `quickstart.md`シナリオ5を`next dev`で手動実行し、未ログイン時のリダイレクト・登録・ログイン・ログアウト・認証必須ページへの到達を確認する — **Docker CLIが無いため`docker compose`は使わず、`flask run`(port 8123)+`API_INTERNAL_URL`指定で`next dev`(port 3123)を直接起動し、`db`サービス(compose networkで到達可能)に接続して実施**。結果: 未ログイン`/timeline`→307で`/login?next=%2Ftimeline`、登録201、ログイン200+`Set-Cookie`(HttpOnly/SameSite=Lax)、ログイン後`/timeline`は200・`/login`は`/timeline`へ307、`/api/me`は200、ログアウト204、ログアウト後`/api/me`は401。**ログアウト後も`/timeline`自体は200(リダイレクトされない)** — これは`proxy.ts`がCookieの「存在」のみ判定するためで、憲章 原則IIIが明記する許容トレードオフ(空の画面が表示されるだけで情報漏洩はない)と一致するため問題なし。テスト用ユーザーは検証後にDBから削除済み。`next build`の成否確認はこのdevcontainer環境では対象外(既知の問題、research.md参照)

**Checkpoint**: この時点でUser Story 1・2が両方独立して動作・検証可能

---

## Phase 5: User Story 3 - 開発者として新規エンドポイントの契約をopenapi.json・型定義に反映する (Priority: P3)

**Goal**: User Story 1で認証を追加したエンドポイントを`openapi.json`と`apps/web`の生成型に反映する(FR-005, FR-006)

**Independent Test**: 生成コマンドを再実行し、`openapi.json`に新エンドポイントが追加されること、`apps/web`側の型生成コマンドを再実行して対応する型が追加されることを確認する

### Implementation for User Story 3

- [X] T023 [US3] `apps/api/app/routes/posts.py`・`goals.py`・`events.py`・`reactions.py`・`calendars.py`の各ビュー関数に、`todos.py`と同形式のapispec向けdocstring(`security: - cookieAuth: []`を含む)を追記する(T006〜T014完了後に実施)
- [X] T024 [US3] `apps/api/generate_openapi.py`に`PostSchema`/`PostCommentSchema`/`GoalSchema`/`GoalCreateSchema`/`GoalMilestoneSchema`/`GoalMilestonePatchSchema`/`CalendarSchema`/`EventSchema`/`ReactionSchema`を`spec.components.schema(...)`で登録し、`view_functions`リストに新規10エンドポイント(実装12ビュー関数、うち`goals`は一覧/作成/マイルストーン更新/削除の4関数で3パスに対応)を追加する(T023に依存)
- [X] T025 [US3] `cd apps/api && python generate_openapi.py`を実行して`openapi.json`を再生成し、再実行しても差分が出ないこと(再現性)を確認する(T024に依存)— 確認済み(2回目の実行結果は`diff`で完全一致)。パスは全17件(既存8+新規10、うち`/api/goals`と`/api/goals/{goal_id}`は別パス)
- [X] T026 [P] [US3] `apps/web`で`npm run generate:api-types`を実行して`src/lib/api-types.generated.ts`を再生成し、既存のregister/login/logout/me/todos型が変わっていないことを`git diff`で確認する(T025に依存、FR-006)— 確認済み。`tsc --noEmit`もエラーなし
- [X] T027 [US3] `apps/api/tests/test_openapi_generation.py`に、新規10パスが生成された`openapi.json`の`paths`に含まれることを検証するアサーションを追加する(T025に依存)
- [X] T028 [US3] `quickstart.md`シナリオ4を実行し、`openapi.json`・生成型の一致を最終確認する(T025〜T027に依存)

**Checkpoint**: 全User Story(P1〜P3)が動作・検証可能

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: 全体の最終確認

- [X] T029 `apps/api`で`python -m pytest`を実行し、既存テスト(`test_auth.py`・`test_todos.py`等)を含めて全件成功することを確認する(T015〜T019, T027に依存)— 27件全パス
- [X] T030 `quickstart.md`の全シナリオ(1〜5)を通しで再実行し、最終確認する(T020, T022, T028に依存)— シナリオ1〜3はpytestスイート、シナリオ4は`generate_openapi.py`再実行+`tsc`、シナリオ5は`flask run`+`next dev`の実HTTPで検証済み。全て期待結果どおり

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: T001, T002は完了済み。T004のみ残
- **Foundational (Phase 2)**: Setup完了後。T005はUser Story実装をブロックしない(ドキュメント整合のみ)が、原則I上先に済ませておく
- **User Story 1 (Phase 3)**: Foundational完了後。他Storyに依存しない。**MVPスコープ**
- **User Story 2 (Phase 4)**: Foundational完了後。US1に依存しない(コード自体はT002で既にマージ済み)。並行着手可能
- **User Story 3 (Phase 5)**: **US1(Phase 3)の完了に依存**する(openapi.jsonはUS1で確定した最終的なエンドポイント仕様を反映するため)
- **Polish (Phase 6)**: 全User Story完了後

### Parallel Opportunities

- Setup: T003(完了済み)、T004
- User Story 1: T006〜T014は対象ファイルが全て異なるため並行実行可能。T015〜T019(テスト)も同様に並行実行可能
- User Story 2とUser Story 3は異なるファイル群(`apps/web`中心 / `apps/api/generate_openapi.py`中心)のため、US1完了後は並行着手可能(US3はUS1のコード内容に依存するため、US1完了は必須)

---

## Parallel Example: User Story 1

```bash
# T006〜T014(ルート実装、対象ファイルが全て異なる)は並行実行可能
Task: "apps/api/app/routes/posts.py に @login_required と calendar_id メンバーシップ確認を追加"
Task: "apps/api/app/routes/goals.py に @login_required と current_user.id への切り替えを追加"
Task: "apps/api/app/routes/events.py に @login_required と is_private フィルタを追加"
Task: "apps/api/app/routes/reactions.py に @login_required を追加"
Task: "apps/api/app/routes/calendars.py に @login_required とメンバーシップ確認を追加"

# T015〜T019(テスト新規作成)も並行実行可能
Task: "apps/api/tests/test_posts.py を新規作成"
Task: "apps/api/tests/test_goals.py を新規作成"
Task: "apps/api/tests/test_events.py を新規作成"
Task: "apps/api/tests/test_reactions.py を新規作成"
Task: "apps/api/tests/test_calendars.py を新規作成"
```

---

## Implementation Strategy

### MVP First (User Story 1のみ)

1. Phase 1: Setup(T004のみ残)
2. Phase 2: Foundational(T005)
3. Phase 3: User Story 1(API認証統合)— これが完了すれば「なりすまし不可能」というfeatureの核心的な価値(SC-001, SC-002)が達成される
4. **STOP and VALIDATE**: quickstart.mdシナリオ1〜3で確認

### Incremental Delivery

1. Setup + Foundational → 基盤整合完了
2. US1(API認証統合)→ 独立検証(MVP到達)
3. US2(Web UI統合)→ 独立検証(US1と並行可能)
4. US3(契約反映)→ US1完了後に着手、独立検証
5. Polish → 全体の最終確認

---

## Notes

- T001・T002・T003は本tasks.md生成前のセッションで既に実施済み(会話履歴参照)。以降のセッションでこのタスクリストを引き継ぐ場合、`git log`で該当マージコミットの存在を確認すれば再実行不要と判断できる
- 憲章 原則III(NON-NEGOTIABLE)により、権限なしの応答は常に404固定(403は使わない)。spec.mdの一部記述(「403または404」)より本憲章を優先する(research.md §2)
- 各タスク完了後にコミットすることを推奨する
- チェックポイントごとに独立して動作確認できる
