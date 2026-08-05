---

description: "Task list template for feature implementation"
---

# Tasks: apiの自動テスト整備

**Input**: Design documents from `/specs/005-api-tests/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md(すべて生成済み)

**Tests**: 本feature自体がテスト整備のため、「テストタスク」と「実装タスク」は一致する
(spec.mdのUser Storyごとにテストファイルを作成する)。

**Organization**: spec.mdのUser Story(P1〜P3)ごとにグルーピングする。

## Format: `[ID] [P?] [Story] Description`

- **[P]**: 並行実行可能(別ファイル・依存なし)
- **[Story]**: US1=認証の回帰検知, US2=todos所有者分離の回帰検知, US3=レート制限の回帰検知

---

## Phase 1: Setup

**Purpose**: pytest導入とテストディレクトリの土台

- [ ] T001 [P] `apps/api/requirements.txt`に`pytest`をバージョン固定で追加する(憲章 原則V)
- [ ] T002 依存を反映する: devコンテナ内で`pip install --user -r apps/api/requirements.txt`(T001に依存)
- [ ] T003 [P] `apps/api/pytest.ini`を新規作成し、`testpaths = tests`を設定する
- [ ] T004 [P] `apps/api/tests/__init__.py`を新規作成する(空ファイル)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: 全User Storyのテストファイルが利用する共通fixture

**⚠️ CRITICAL**: このフェーズ完了までUser Storyのテストは書けない

- [ ] T005 `apps/api/tests/conftest.py`に`app`fixtureを実装する(`create_app()`を呼び、テスト用の`SECRET_KEY`等が環境変数として既に用意されていることを前提とする)(T002に依存)
- [ ] T006 `apps/api/tests/conftest.py`に、research.md §2で決定したSAVEPOINTベースのトランザクションfixture(autouse)を実装する。テスト前に`db.engine.connect()`でトランザクションとネストしたSAVEPOINTを開始し、`db.session`をそのconnectionにbindする。テスト後に必ずrollbackし、開発用DBにデータを残さない(T005に依存)
- [ ] T007 `apps/api/tests/conftest.py`に、`limiter`のストレージをテストごとにリセットするfixture(autouse)を実装する。research.md §3のとおり、テスト間でログイン試行回数が引き継がれないようにする(T005に依存)
- [ ] T008 [P] `apps/api/tests/conftest.py`に`client`fixture(`app.test_client()`を返す)を実装する(T005に依存)
- [ ] T009 [P] `apps/api/tests/conftest.py`に、テスト用利用者を作成するヘルパー関数`create_user(email, password, display_name)`を実装する(data-model.mdのテスト用利用者の形に従う)(T006に依存)

**Checkpoint**: ここまで完了すればUser Storyのテストを書き始められる

---

## Phase 3: User Story 1 - 開発者として認証機能の回帰を自動で検知する (Priority: P1) 🎯 MVP

**Goal**: `quickstart.md`シナリオ1〜3(登録・ログイン・ログアウト・`/api/me`・重複登録拒否・ログイン失敗の一律エラー)を自動テスト化する

**Independent Test**: `apps/api/tests/test_auth.py`のみを実行し、全テストがパスすることを確認する

### Implementation for User Story 1

- [ ] T010 [P] [US1] `apps/api/tests/test_auth.py`に登録成功のテストを実装する(FR-001)。未登録メールで`POST /api/register`を呼び、201とレスポンス形式(`password_hash`を含まない)を検証する
- [ ] T011 [P] [US1] `apps/api/tests/test_auth.py`に重複登録拒否のテストを実装する(FR-002)。同一メールで2回登録し、2回目が400 `invalid_request`になることを検証する
- [ ] T012 [P] [US1] `apps/api/tests/test_auth.py`にログイン成功と`/api/me`のテストを実装する(FR-003, FR-006)。登録済みの利用者でログインし、`client`のCookieが引き継がれた状態で`/api/me`が200・本人の情報を返すことを検証する
- [ ] T013 [P] [US1] `apps/api/tests/test_auth.py`にログイン失敗時の一律エラーのテストを実装する(FR-008)。存在しないメールでのログインと、登録済みメール+誤パスワードでのログインの両方が同一のレスポンスボディ・同一の401になることを検証する
- [ ] T014 [P] [US1] `apps/api/tests/test_auth.py`にログアウトのテストを実装する(FR-005, FR-007)。ログイン後にログアウトし、204が返ること、以降の`/api/me`が401になることを検証する

**Checkpoint**: 認証機能の回帰が単独で検知可能

---

## Phase 4: User Story 2 - 開発者としてtodosの所有者分離の回帰を自動で検知する (Priority: P2)

**Goal**: `quickstart.md`シナリオ5(todosの認証必須化と所有者分離)を自動テスト化する

**Independent Test**: `apps/api/tests/test_todos.py`のみを実行し、全テストがパスすることを確認する

### Implementation for User Story 2

- [ ] T015 [US2] `apps/api/tests/test_todos.py`に未ログイン時の拒否テストを実装する(FR-005)。未ログインで`GET /api/todos`, `POST /api/todos`を呼び、いずれも401になることを検証する(T009に依存)
- [ ] T016 [US2] `apps/api/tests/test_todos.py`に所有者分離のテストを実装する(FR-006)。利用者Aと利用者Bをそれぞれ作成し、Aが自分のTodoを作成後、Bとしてログインして一覧・詳細取得してもAのTodoが含まれない・404になることを検証する(T009, T015に依存)
- [ ] T017 [US2] `apps/api/tests/test_todos.py`に、自分のTodoに対するCRUD(作成・一覧・更新・削除)が成功することのテストを実装する(既存の`quickstart.md`シナリオ5相当)(T016に依存)

**Checkpoint**: todosの所有者分離の回帰が単独で検知可能

---

## Phase 5: User Story 3 - 開発者としてレート制限の回帰を自動で検知する (Priority: P3)

**Goal**: `quickstart.md`シナリオ4(ログイン試行のレート制限)を自動テスト化する

**Independent Test**: `apps/api/tests/test_auth_rate_limit.py`のみを実行し、全テストがパスすることを確認する

### Implementation for User Story 3

- [ ] T018 [US3] `apps/api/tests/test_auth_rate_limit.py`にレート制限のテストを実装する(FR-004)。同一送信元から`POST /api/login`を規定回数(research.md参照。既存実装は5回/分)を超えて呼び、超過分が429になることを検証する。T007のリセットfixtureにより他テストの試行回数と干渉しないことを前提にする(T007に依存)

**Checkpoint**: 全User Story(P1〜P3)の回帰が自動検知可能

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: ドキュメント整合とテストスイート全体の最終確認

- [ ] T019 [P] `apps/api/README.md`に「テストの実行方法」節を追加する(quickstart.mdの手順を要約して転記)
- [ ] T020 `apps/api`ディレクトリで`python -m pytest`を実行し、全テストがパスすることを確認する(T010〜T018に依存)
- [ ] T021 `quickstart.md`の「テスト後のDB確認」手順を実行し、テスト実行前後で`users`/`todos`の件数が変化しないことを確認する(T020に依存)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: 依存なし。即着手可
- **Foundational (Phase 2)**: Setup完了後。**全User Storyをブロックする**
- **User Stories (Phase 3-5)**: Foundational完了後。spec.mdの優先度順(P1→P2→P3)に実施することを推奨するが、US1/US2/US3はそれぞれ別ファイルのため並行も可能
- **Polish (Phase 6)**: 全User Story完了後

### User Story Dependencies

- **US1(認証, P1)**: Foundational完了後に開始可。他Storyに依存しない
- **US2(todos所有者分離, P2)**: Foundational完了後に開始可。US1に依存しない(別ファイル・別fixtureのため)
- **US3(レート制限, P3)**: Foundational完了後に開始可。US1のログインエンドポイントを叩くが、テストコードとしてはUS1のテストファイルに依存しない

### Parallel Opportunities

- Setup: T001, T003, T004は並行実行可能
- Foundational: T008, T009は並行実行可能(T006, T007完了後)
- User Story 1: T010〜T014は同一ファイル内だが、テスト関数が独立しているため並行に書き進めてよい
- Polish: T019は他タスクと並行可能

---

## Parallel Example: Foundational Phase

```bash
# T005完了後、以下は並行実行可能
Task: "apps/api/tests/conftest.py に client fixture を実装"
Task: "apps/api/tests/conftest.py に create_user ヘルパーを実装"
```

---

## Implementation Strategy

### MVP First (User Story 1)

1. Phase 1: Setup
2. Phase 2: Foundational(**必須、全Storyをブロック**)
3. Phase 3: US1(認証) — ここまでで最もセキュリティ影響の大きい認証機能の回帰検知が完成
4. **STOP and VALIDATE**: `python -m pytest apps/api/tests/test_auth.py`

### Incremental Delivery

1. Setup + Foundational → 基盤完成
2. US1(認証)→ 独立検証(MVP到達)
3. US2(todos所有者分離)→ 独立検証
4. US3(レート制限)→ 独立検証
5. Polish(ドキュメント整合・全体の最終確認)

---

## Notes

- 本featureでは「テストを先に書いて失敗を確認する」というTDDのプロセスは適用しない(対象コードは`003-user-auth`で実装済みのため、テストは最初からパスすることが期待される)。
- 各タスク完了後にコミットすることを推奨する。
- チェックポイントごとに独立して動作確認できる。
