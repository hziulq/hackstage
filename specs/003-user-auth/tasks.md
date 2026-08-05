---

description: "Task list template for feature implementation"
---

# Tasks: ユーザー認証(ログイン・ログアウト)

**Input**: Design documents from `/specs/003-user-auth/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/auth-api.md, quickstart.md（すべて生成済み）

**Tests**: 自動テストは本feature範囲外（別feature `005-api-tests` で整備する方針をこの会話で確定済み）。検証は各Phaseで `quickstart.md` の該当シナリオを手動実行する。

**Organization**: spec.mdのUser Story（P1〜P3）ごとにグルーピング。加えて、本feature実装の副作用として解消する `apps/api/app/routes/todos.py` の暫定実装修正をPolishフェーズに含む。

## Format: `[ID] [P?] [Story] Description`

- **[P]**: 並行実行可能（別ファイル・依存なし）
- **[Story]**: US1=登録, US2=ログイン, US3=ログアウト, US4=レート制限

---

## Phase 1: Setup

**Purpose**: 依存ライブラリの追加と反映

- [X] T001 [P] `apps/api/requirements.txt` に `Flask-Login`, `argon2-cffi`, `Flask-Limiter` をバージョン固定で追加する（憲章 原則V: 依存バージョン固定）
- [X] T002 依存を反映する: devコンテナ内で `pip install --user -r apps/api/requirements.txt`、ホスト側で `docker compose build api && docker compose up -d api`（`apps/api/README.md` の手順に従う。T001に依存）— **devコンテナ側のpip installのみ本セッションで実施済み。dockerコマンドはこの環境から実行できないため、`api`コンテナの再ビルドはユーザー側で実施が必要**

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: 全User Storyが依存する共通基盤。ここが終わるまでどのUser Storyも着手できない

**⚠️ CRITICAL**: このフェーズ完了までUser Story実装を開始しない

- [X] T003 [P] `apps/api/app/auth/__init__.py` と `apps/api/app/auth/security.py` を新規作成し、`argon2.PasswordHasher` を使う `hash_password()` / `verify_password()` を実装する（T002に依存）
- [X] T004 `apps/api/app/models/user.py` の `User` に `UserMixin`（flask_login）を継承させ、T003の `security.py` を使う `set_password()` / `check_password()` メソッドを追加する（T003に依存）
- [X] T005 [P] `apps/api/app/schemas/user.py` を新規作成し、`RegisterSchema`（email/password/display_name）、`LoginSchema`（email/password）、`UserSchema`（出力用。`password_hash` を含めない）を定義する（T002に依存）
- [X] T006 [P] `apps/api/app/extensions.py` に `login_manager = LoginManager()` と `limiter = Limiter(key_func=get_remote_address)` を追加し、「Flask-Login未導入」の既存コメントを削除する（T002に依存）
- [X] T007 `apps/api/app/__init__.py` で `login_manager.init_app(app)` / `limiter.init_app(app)`、`@login_manager.user_loader`（idからUserをロード）、`login_manager.unauthorized_handler`（リダイレクトではなく `{"error":{"code":"unauthorized",...}}` + 401 のJSONを返す）を実装する（T004, T006に依存）
- [X] T008 [P] `docs/design.md` §7 の認証系エンドポイント表に `POST /api/register` を追記する（憲章 原則I: 設計値の変更は実装前に先に文書を更新する MUST）

**Checkpoint**: ここまで完了すればUser Story実装を開始できる

---

## Phase 3: User Story 1 - 新しい利用者としてアカウントを作る (Priority: P1) 🎯 MVP

**Goal**: メール・パスワード・表示名によるオープン登録(FR-001)。重複メールは拒否(FR-002)

**Independent Test**: 未登録メールで登録APIを呼び、成功すること。同じメールで再度登録すると拒否されること

### Implementation for User Story 1

- [X] T009 [US1] `apps/api/app/routes/auth.py` を新規作成し、`Blueprint("auth", url_prefix="/api")` と `POST /api/register` を実装する（`RegisterSchema`で検証、`User.query.filter_by(email=...)`で重複チェック→400、`User.set_password()`でハッシュ化して保存、201で`UserSchema`を返す。contracts/auth-api.md参照）（T005, T007に依存）
- [X] T010 [US1] `apps/api/app/__init__.py` に `auth_bp` を登録する（`app.register_blueprint(auth_bp)`）（T009に依存）
- [X] T011 [US1] `quickstart.md` シナリオ1手順1・シナリオ2を実行し、登録成功と重複拒否を確認する（T010に依存）— **`docker`コマンドがこの環境から使えないため、`curl`ではなくFlaskの`test_client()`で実施。結果: 201登録成功、重複メールは400 `invalid_request`。実施後にテストデータは削除済み**

**Checkpoint**: 登録機能が単独で動作・検証可能

---

## Phase 4: User Story 2 - 登録済みユーザーとしてログインする (Priority: P1)

**Goal**: メール・パスワードでの認証(FR-003)、7日間のセッション維持(FR-004)、`/api/me`での自分の情報取得(FR-006)、失敗時の一律エラー(FR-008)

**Independent Test**: 登録済みのメール・パスワードでログインし、以降 `/api/me` で自分の情報が取れること。存在しないメール／誤ったパスワードのどちらでも同一のエラーになること

### Implementation for User Story 2

- [X] T012 [US2] `apps/api/app/routes/auth.py` に `POST /api/login` を実装する（`LoginSchema`で検証、`User.check_password()`で照合、成功時は`login_user()`＋`session.permanent = True`でセッション確立、失敗時はメール不存在・パスワード誤りを区別しない一律の401「invalid_credentials」を返す。レート制限は T017 で付与）（T010に依存）
- [X] T013 [US2] `apps/api/app/routes/auth.py` に `GET /api/me` を実装する（`@login_required`、`UserSchema`で`current_user`をdumpして返す）（T010に依存）
- [X] T014 [US2] `quickstart.md` シナリオ1手順2-3・シナリオ3を実行し、ログイン成功と失敗時の一律エラーを確認する（T012, T013に依存）— test_clientで実施。ログイン成功時200、存在しないメール／誤パスワードのレスポンスbodyが完全一致することを確認

**Checkpoint**: 登録・ログイン・`/api/me`が一連で動作・検証可能

---

## Phase 5: User Story 3 - ログアウトして識別状態を終了する (Priority: P2)

**Goal**: 明示的なログアウト(FR-005)。ログアウト後は未ログイン状態として扱われる(FR-007)

**Independent Test**: ログイン後にログアウトを呼び、以降 `/api/me` が401になること

### Implementation for User Story 3

- [X] T015 [US3] `apps/api/app/routes/auth.py` に `POST /api/logout` を実装する（`@login_required`、`logout_user()`、204を返す）（T010に依存）
- [X] T016 [US3] `quickstart.md` シナリオ1手順4-5を実行し、ログアウトと未ログイン401を確認する（T015に依存）— test_clientで実施。ログアウト204、以降の`/api/me`は401

**Checkpoint**: 登録・ログイン・ログアウトの一連の流れが動作・検証可能

---

## Phase 6: User Story 4 - 不正なログイン試行から保護される (Priority: P3)

**Goal**: ログイン試行のレート制限(FR-009, SC-004)

**Independent Test**: 同一送信元から短時間に繰り返しログインを試み、一定回数超過後に制限されること

### Implementation for User Story 4

- [X] T017 [US4] `apps/api/app/routes/auth.py` の `POST /api/login` に `@limiter.limit("5 per minute")` を付与する（research.md §3のレート値・トレードオフを参照）（T012に依存）
- [X] T018 [US4] `quickstart.md` シナリオ4を実行し、6回目以降で429になることを確認する（T017に依存）— test_clientで実施。1〜5回目は401、6回目は429を確認

**Checkpoint**: 全User Story(P1〜P3)が動作・検証可能

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: `todos.py`の暫定実装解消（この会話で確定した本feature内スコープ）とドキュメント整合

- [X] T019 [P] `apps/api/app/schemas/todo.py` から `user_id` フィールドを削除する（クライアント指定を受け付けない）— `load`時は受け付けず、出力用に`dump_only=True`として残した(所有者をレスポンスで確認できるようにするため)
- [X] T020 `apps/api/app/routes/todos.py` の全エンドポイント（list/get/create/update/delete）に `@login_required` を付与し、`request.args.get("user_id")` を `current_user.id` に置き換える。作成時は `Todo(user_id=current_user.id, ...)` とする（T007, T019に依存）
- [X] T021 [P] `apps/api/README.md` の「認証について」節を更新し、「Flask-Loginはまだ入れていない」という記述を実装済みの内容に修正する
- [X] T022 `quickstart.md` シナリオ5を実行し、`/api/todos` の認証必須化を確認する（T020に依存）— test_clientで実施。未ログインは401、ログイン後は自分のTodoの作成・一覧取得が成功
- [X] T023 `quickstart.md` の全シナリオ(1〜5)を通しで再実行し、最終確認する（T011, T014, T016, T018, T022に依存）— 全シナリオpass。作成したテストデータ(user/todo)はセッション終了後にDBから削除済み

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: 依存なし。即着手可
- **Foundational (Phase 2)**: Setup完了後。**全User Storyをブロックする**
- **User Stories (Phase 3-6)**: Foundational完了後。spec.mdの優先度順(P1→P1→P2→P3)に実施することを推奨するが、US1/US2/US3/US4はそれぞれ独立ファイル操作が中心のため、人員が複数いれば並行も可能
- **Polish (Phase 7)**: 全User Story完了後（T020が認証基盤(T007)とUser Story群の完了を前提とするため）

### User Story Dependencies

- **US1（登録, P1）**: Foundational完了後に開始可。他Storyに依存しない
- **US2（ログイン, P1）**: Foundational完了後に開始可。`auth_bp`登録(T010)はUS1で行うため、実質US1のBlueprint作成後に着手
- **US3（ログアウト, P2）**: US2と同様、T010完了後に着手可能。US2の完了を待つ必要はない（同じファイルへの追記のため実務上は順次が安全）
- **US4（レート制限, P3）**: US2のログイン実装(T012)に対する追加のため、T012完了後

### Parallel Opportunities

- Foundational: T003, T005, T006, T008 は並行実行可能（T004はT003完了後、T007はT004・T006完了後）
- Polish: T019, T021 は並行実行可能

---

## Parallel Example: Foundational Phase

```bash
# T002完了後、以下は並行実行可能
Task: "apps/api/app/auth/security.py に argon2 ハッシュ関数を実装"
Task: "apps/api/app/schemas/user.py に Register/Login/UserSchema を実装"
Task: "apps/api/app/extensions.py に login_manager, limiter を追加"
Task: "docs/design.md §7 に POST /api/register を追記"
```

---

## Implementation Strategy

### MVP First (User Story 1 + 2)

1. Phase 1: Setup
2. Phase 2: Foundational（**必須、全Storyをブロック**）
3. Phase 3: US1（登録）
4. Phase 4: US2（ログイン・`/api/me`）— ここまでで「アカウントを作りログインして自分の情報を見る」という最小価値が完成
5. **STOP and VALIDATE**: quickstart.md シナリオ1〜3で確認

### Incremental Delivery

1. Setup + Foundational → 基盤完成
2. US1（登録）→ 独立検証
3. US2（ログイン・me）→ 独立検証（MVP到達）
4. US3（ログアウト）→ 独立検証
5. US4（レート制限）→ 独立検証
6. Polish（todos.py修正・ドキュメント整合）→ 全体の最終検証

---

## Notes

- テストタスクは含まない（自動テスト整備は`005-api-tests`に分離。本featureは`quickstart.md`の手動シナリオで検証する）
- `todos.py`の修正はspec.mdのUser Storyではないため、Polishフェーズに配置した（この会話で確定したfeatureスコープ）
- 各タスク完了後にコミットすることを推奨する
- チェックポイントごとに独立して動作確認できる
