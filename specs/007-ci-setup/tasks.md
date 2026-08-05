---

description: "Task list template for feature implementation"
---

# Tasks: CI(Lint/テスト/openapi.json生成チェック)の整備

**Input**: Design documents from `/specs/007-ci-setup/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md(すべて生成済み)

**Tests**: 本feature自体はCI定義の追加であり、`quickstart.md`のローカル再現手順で検証する。
新規のpytestテストは追加しない。

**Organization**: spec.mdのUser Story(P1〜P2)ごとにグルーピングする。

## Format: `[ID] [P?] [Story] Description`

- **[P]**: 並行実行可能(別ファイル・依存なし)
- **[Story]**: US1=Lint/テスト結果の可視化, US2=openapi.json生成漏れの検知

---

## Phase 1: Setup

**Purpose**: ruffの導入とローカル動作確認の土台

- [ ] T001 [P] `apps/api/pyproject.toml`を新規作成し、`[tool.ruff]`で対象を`apps/api`配下に限定する(最小構成)
- [ ] T002 devコンテナ内で`pip install --user ruff`し、`ruff check apps/api`が既存コードに対してエラー無く完了することを確認する(T001に依存)

---

## Phase 2: User Story 1 - 開発者としてPR上でLint・テストの結果を確認できる (Priority: P1) 🎯 MVP

**Goal**: PR上にLintとテストの結果が非ブロッキングで表示される

**Independent Test**: PRを作成し、GitHub Actions上に`lint`/`test`ジョブの結果が表示され、失敗してもマージ可能なことを確認する

### Implementation for User Story 1

- [ ] T003 [US1] `.github/workflows/api-ci.yml`を新規作成し、`pull_request`トリガーで`lint`ジョブ(`ruff check apps/api`)を実装する(T002に依存)
- [ ] T004 [US1] `.github/workflows/api-ci.yml`に`test`ジョブを追加する。`services`で`postgres:17`を起動し、`DATABASE_URL`/`SECRET_KEY`をCI用のダミー値で設定した上で`apps/api`の依存をインストールし`python -m pytest`を実行する(T003に依存)
- [ ] T005 [US1] ローカルで`quickstart.md`の「Lintジョブの再現」「テストジョブの再現」を実行し、CIワークフローと同じコマンドがdevコンテナ内で成功することを確認する(T004に依存)

**Checkpoint**: Lint・テストの結果がPR上で確認できる状態になる

---

## Phase 3: User Story 2 - 開発者としてopenapi.jsonの生成漏れに気づける (Priority: P2)

**Goal**: openapi.json生成差分がPR上で非ブロッキングに表示される

**Independent Test**: エンドポイントを変更してopenapi.jsonを再生成せずにPRを作り、`openapi-check`ジョブの結果から食い違いが分かることを確認する

### Implementation for User Story 2

- [ ] T006 [US2] `.github/workflows/api-ci.yml`に`openapi-check`ジョブを追加する。`python generate_openapi.py`を実行後、`git diff --exit-code openapi.json`のステップに`continue-on-error: true`を付与し、差分があっても⚠️表示のままジョブ・ワークフロー全体は成功させる(T004に依存)
- [ ] T007 [US2] ローカルで`quickstart.md`の「openapi.json生成差分チェックジョブの再現」を実行し、差分が無いこと(終了コード0)を確認する(T006に依存)

**Checkpoint**: 3ジョブ(lint/test/openapi-check)すべてがCI上で動作する

---

## Phase 4: Polish & Cross-Cutting Concerns

**Purpose**: ドキュメント整合と最終確認

- [ ] T008 CONTRIBUTING.mdの既存の「CI」節(§3、憲章改定時に追加済み)を確認し、ワークフローファイルのパス(`.github/workflows/api-ci.yml`)と食い違いがないか確認する。食い違いがあれば修正する
- [ ] T009 本featureのブランチをpushしてPRを作り、`quickstart.md`の「PRでの確認」手順を実行して3ジョブの表示・非ブロッキング動作を確認する(T005, T007に依存)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: 依存なし。即着手可
- **User Story 1 (Phase 2)**: Setup完了後
- **User Story 2 (Phase 3)**: User Story 1完了後(同じワークフローファイルへの追記のため実務上は順次が安全)
- **Polish (Phase 4)**: 全User Story完了後

### User Story Dependencies

- **US1(Lint/テストの可視化, P1)**: Setup完了後に開始可。他Storyに依存しない
- **US2(生成漏れの検知, P2)**: US1で作成した`api-ci.yml`に追記するため、US1完了後

### Parallel Opportunities

- Setup: T001は単独タスク
- 本feature全体が単一ファイル(`.github/workflows/api-ci.yml`)への追記が中心のため、並行実行できるタスクは少ない

---

## Implementation Strategy

### MVP First (User Story 1)

1. Phase 1: Setup
2. Phase 2: US1(Lint/テストの可視化)— ここまででCIの最小価値(結果が見える)が完成
3. **STOP and VALIDATE**: PRを作ってGitHub Actions上の表示を確認

### Incremental Delivery

1. Setup → ruff導入確認
2. US1(Lint/テスト)→ 独立検証(MVP到達)
3. US2(openapi.json生成漏れ検知)→ 独立検証
4. Polish(ドキュメント整合・PRでの最終確認)

---

## Notes

- 各タスク完了後にコミットすることを推奨する。
- 実際のGitHub Actions実行結果の確認(T009)は、このfeatureブランチをpushしPRを作らないと検証できない。
