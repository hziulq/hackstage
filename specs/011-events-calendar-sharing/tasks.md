---

description: "Task list template for feature implementation"
---

# Tasks: グループカレンダーの作成・共有と予定作成

**Input**: Design documents from `/specs/011-events-calendar-sharing/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/calendars-events-api.md, quickstart.md(すべて生成済み)

**Tests**: `010-secure-social-api`で確立済みのpytestパターン(`tests/conftest.py`の`create_user`/`client`フィクスチャ)に従い、各User Storyにテストタスクを含める。

**Organization**: spec.mdのUser Story(P1〜P3)ごとにグルーピング。

## Format: `[ID] [P?] [Story] Description`

- **[P]**: 並行実行可能(別ファイル・依存なし)
- **[Story]**: US1=グループ作成, US2=招待コード参加, US3=予定作成, US4=Web UI接続

---

## Phase 1: Setup

**Purpose**: 本feature共通のスキーマ追加

- [X] T001 [P] `apps/api/app/schemas/calendar.py`に`CalendarCreateSchema`(`name`必須、1〜100文字)・
  `CalendarJoinSchema`(`invite_code`必須、1〜32文字)を追加する

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: US1・US2が共通で使う招待コード生成ヘルパー

**⚠️ CRITICAL**: このフェーズ完了までUser Story 1・2の実装を開始しない

- [X] T002 `apps/api/app/routes/calendars.py`に`_generate_invite_code()`(`secrets.token_urlsafe(6)`、
  `Calendar.invite_code`との衝突時は最大10回リトライ、research.md §1参照)を追加する

**Checkpoint**: ここまで完了すればUser Story 1(グループ作成)を開始できる

---

## Phase 3: User Story 1 - 利用者としてグループを作り仲間を招待する (Priority: P1) 🎯 MVP

**Goal**: グループカレンダーを作成し、招待コードを発行する(FR-001, FR-002)

**Independent Test**: グループ名を指定してグループを作成し、レスポンスに招待コードが含まれること、
作成者が参加者一覧に表示されることを確認する

### Implementation for User Story 1

- [X] T003 [US1] `apps/api/app/routes/calendars.py`に`POST /api/calendars`
  (`create_group_calendar`)を追加する。`CalendarCreateSchema`で検証、`Calendar(name=..., type="group",
  owner_id=current_user.id, invite_code=_generate_invite_code())`を作成、`flush`後に
  `CalendarMember(calendar_id=..., user_id=current_user.id, role="owner")`を追加、`201`で
  `CalendarSchema`を返す(T001, T002に依存)

### Tests for User Story 1

- [X] T004 [P] [US1] `apps/api/tests/test_calendars.py`に、未ログイン401・グループ作成で
  `invite_code`が発行されること・作成者が`members`一覧に`role=owner`で表示されることを検証する
  テストを追加する

- [X] T005 [US1] `quickstart.md`シナリオ1を実行し、グループ作成と招待コード発行を確認する
  (T003, T004に依存) — 完了。docker/curlの代わりに flask run + next dev を直接起動して実HTTPで確認

**Checkpoint**: グループ作成が単独で動作・検証可能

---

## Phase 4: User Story 2 - 利用者として招待コードでグループに参加する (Priority: P1)

**Goal**: 招待コードで既存グループに参加する。無効なコードは拒否、重複参加は冪等(FR-003〜FR-005)

**Independent Test**: 有効な招待コードで別の利用者が参加し、参加者一覧に追加されることを確認する

### Implementation for User Story 2

- [X] T006 [US2] `apps/api/app/routes/calendars.py`に`POST /api/calendars/join`
  (`join_group_calendar`)を追加する。`CalendarJoinSchema`で検証、`Calendar.query.filter_by(
  invite_code=..., type="group")`で検索(無ければ404 `not_found`)、既存の`CalendarMember`が
  あれば`200`、無ければ`role="member"`で作成して`201`を返す(T001, T003に依存)

### Tests for User Story 2

- [X] T007 [P] [US2] `apps/api/tests/test_calendars.py`に、無効な招待コードは404・有効な
  招待コードでの参加は201・同じコードでの再参加は200(重複作成されない)ことを検証するテストを
  追加する

- [X] T008 [US2] `quickstart.md`シナリオ2を実行し、招待コード参加・無効コード拒否・冪等性を
  確認する(T006, T007に依存) — 完了。実HTTPで無効コード404・冪等な再参加200を確認

**Checkpoint**: グループ作成・参加が一連で動作・検証可能(グループ機能のMVP)

---

## Phase 5: User Story 3 - グループのメンバーとして予定を作成・共有する (Priority: P2)

**Goal**: グループの参加者が予定を作成できる。非参加者は拒否、非公開予定は本人以外に見えない
(FR-006, FR-007)

**Independent Test**: 参加者が予定を作成し他の参加者から見えること、非公開指定した予定は
本人以外から見えないことを確認する

### Implementation for User Story 3

- [X] T009 [US3] `apps/api/app/routes/events.py`に`POST /api/events`(`create_event`)を追加する。
  `EventSchema`で検証、`is_calendar_member(data["calendar_id"], current_user.id)`で参加確認
  (非参加者は404)、`Event(user_id=current_user.id, **data)`を作成し`201`で返す

### Tests for User Story 3

- [X] T010 [P] [US3] `apps/api/tests/test_events.py`に、未ログイン401・非参加者からの作成は404・
  作成した予定が`GET /api/events`の一覧に反映されること・非公開予定が他の参加者の一覧に
  出現しないことを検証するテストを追加する(既存の`test_private_events_hidden_from_other_members`
  はDB直接投入だったため、実際にAPI経由で作成する形に寄せる)

- [X] T011 [US3] `quickstart.md`シナリオ3を実行し、予定作成・非公開フィルタ・非参加者拒否を
  確認する(T009, T010に依存) — 完了。非公開予定が他メンバーの一覧に出現しないことを実HTTPで確認

**Checkpoint**: グループ作成・参加・予定作成がすべて単独で動作・検証可能

---

## Phase 6: User Story 4 - 開発者としてグループ画面を実データに接続する (Priority: P3)

**Goal**: `apps/web`の`timeline`(group scope)・`mypage`をモックからUser Story 1〜3のAPIに
繋ぎ替える(FR-010)

**Independent Test**: ブラウザでグループを作成し、招待コードを別ユーザーで入力して参加し、
両者の画面に互いの予定・メンバー情報が反映されることを確認する

### Implementation for User Story 4

- [X] T012 [P] [US4] `apps/api/generate_openapi.py`に`CalendarCreateSchema`・`CalendarJoinSchema`を
  登録し、`view_functions`に`calendars.create_group_calendar`・`calendars.join_group_calendar`・
  `events.create_event`を追加する。`cd apps/api && python generate_openapi.py`で`openapi.json`を
  再生成し、`apps/web`で`npm run generate:api-types`を実行する(T003, T006, T009に依存)
- [X] T013 [P] [US4] `apps/web/src/lib/calendars.ts`に`create(name)`・`join(inviteCode)`を追加する
  (T012に依存)
- [X] T014 [P] [US4] `apps/web/src/lib/events.ts`に`create(input)`を追加する(T012に依存)
- [X] T015 [P] [US4] `apps/web/src/lib/group.ts`を新規作成し、「自分の所属グループの
  calendar_id」をブラウザのlocalStorageで保持する`useGroupCalendarId()`フックを実装する
  (research.md §5の設計方針。`mypage`・`timeline`の両ページで共有する)
- [X] T016 [US4] `apps/web/src/components/mypage/InviteCodeCard.tsx`を、所属グループが無い場合は
  グループ作成フォーム+招待コード参加フォームを表示し、所属済みの場合は既存の招待コード表示+
  コピー機能を維持する形に改修する(T013, T015に依存)
- [X] T017 [US4] `apps/web/src/app/mypage/page.tsx`を、`useGroupCalendarId()`で取得した
  `calendar_id`があれば`GET /api/calendars/{id}`・`GET /api/calendars/{id}/members?sort=score`を
  呼び、`InviteCodeCard`・`RankingList`に実データを渡す形に改修する(T016に依存)
- [X] T018 [US4] `apps/web/src/components/timeline/`に予定作成用の新規コンポーネント
  `NewEventForm.tsx`(タイトル・日時・カテゴリ・非公開チェックボックス)を追加する(events作成の
  UIが従来存在しないため)
- [X] T019 [US4] `apps/web/src/app/timeline/page.tsx`のgroup scopeを、`useGroupCalendarId()`の
  `calendar_id`を使って`eventsClient.list`・`postsClient.list(category:"timeline",scope:"group")`・
  `reactionsClient`(personal scope実装と同じパターン)に接続する。`NewEventForm`から
  `eventsClient.create`を呼べるようにする(T014, T015, T018に依存)

### Tests for User Story 4

- [X] T020 [US4] `quickstart.md`シナリオ5をブラウザ(2ユーザー)で実行し、グループ作成→招待コード
  共有→参加→予定作成→両者の画面反映を確認する(T016〜T019に依存) — 完了。ブラウザ操作ではなく
  next dev + flask run への実HTTPで2ユーザー分のフローを確認(内容はシナリオ5と同等)。
  `/mypage`・`/timeline`ともに200でエラーなくレンダリングされることを確認。テストデータは削除済み

**Checkpoint**: 全User Story(P1〜P3)がAPI・Web UI双方で動作・検証可能

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: 全体の最終確認

- [X] T021 `docs/design.md` §7の画面別エンドポイント表(Timeline・Mypage)に本featureの
  新規エンドポイントを追記する(憲章 原則I)
- [X] T022 `apps/api`で`python -m pytest`を実行し、既存テストを含めて全件成功することを確認する
  (T004, T007, T010に依存) — 38件全パス
- [X] T023 `quickstart.md`の全シナリオ(1〜5)を通しで再実行し、最終確認する
  (T005, T008, T011, T020に依存) — 完了。シナリオ1〜3はpytest(38件)、シナリオ4は
  `generate_openapi.py`再実行(差分なし・再現性確認済み)+`tsc --noEmit`、シナリオ5は
  実HTTPでのE2E確認

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: 依存なし
- **Foundational (Phase 2)**: Setup完了後。US1・US2をブロックする
- **User Story 1 (Phase 3)**: Foundational完了後。**MVPスコープ**
- **User Story 2 (Phase 4)**: US1完了後(参加対象のグループがUS1で作られるため)
- **User Story 3 (Phase 5)**: US1・US2に依存しない(既存の個人カレンダーでも予定作成のテストは
  可能)が、グループでの共有価値を確認するにはUS1・US2が先に必要
- **User Story 4 (Phase 6)**: US1〜US3すべてのAPIが揃った後に着手
- **Polish (Phase 7)**: 全User Story完了後

### Parallel Opportunities

- User Story 4: T013・T014・T015は対象ファイルが異なるため並行実行可能。T012(openapi生成)は
  US1〜US3のルート実装完了後であれば先行して実行できる

---

## Implementation Strategy

### MVP First (User Story 1 + 2)

1. Phase 1: Setup
2. Phase 2: Foundational
3. Phase 3: User Story 1(グループ作成)
4. Phase 4: User Story 2(招待コード参加)
5. **STOP and VALIDATE**: quickstart.mdシナリオ1〜2で確認 — ここまでで「グループを作って
   共有する」という最小価値が完成

### Incremental Delivery

1. Setup + Foundational → 基盤完成
2. US1(グループ作成)→ 独立検証
3. US2(招待コード参加)→ 独立検証(MVP到達)
4. US3(予定作成)→ 独立検証
5. US4(Web UI接続)→ ブラウザでの最終確認
6. Polish → 全体の最終確認

---

## Notes

- 憲章 原則III(NON-NEGOTIABLE)により、権限なし・無効な招待コードの応答は常に404固定
  (403は使わない)
- 各タスク完了後にコミットすることを推奨する
- チェックポイントごとに独立して動作確認できる
