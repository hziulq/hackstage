# Feature Specification: openapi.jsonの生成

**Feature Branch**: `006-openapi-generation`

**Created**: 2026-08-05

**Status**: Draft

**Input**: User description: "憲章 原則V・docs/design.md §7で必須とされているopenapi.jsonが未生成。apiが生成してリポジトリにコミットし、webがそこからTypeScript型を生成する起点にする。認証・エンドポイント実装(003-user-auth)と並行して整備しないとフロント連携が手戻りになりやすいという課題が過去に指摘されている。現時点で実装済みのエンドポイント(/api/health, /api/hello, /api/register, /api/login, /api/logout, /api/me, /api/todosのCRUD)を対象に、apiがOpenAPIスキーマを生成できる状態にする。"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 開発者としてAPIの契約を生成物として得る (Priority: P1)

開発者(バックエンド担当)が、`apps/api`のコードを変更した後、1コマンドで最新の`openapi.json`を再生成し、
実装と食い違いのない契約をリポジトリにコミットできる。

**Why this priority**: 憲章 原則V(契約駆動の境界)で`api`は`openapi.json`を生成してコミットするMUSTと
定められているが、現時点で1件も生成されていない。フロントエンド(`apps/web`)がAPI型を手書きすると
`web`側で二重管理が発生し、後から実装と食い違う。

**Independent Test**: `apps/api`で生成コマンドを実行し、`openapi.json`が更新されること、そこに実装済みの
全エンドポイントが含まれることを確認すれば、単独で価値を検証できる。

**Acceptance Scenarios**:

1. **Given** `apps/api`の実装済みエンドポイント一式がある、**When** 生成コマンドを実行する、**Then** `openapi.json`が生成され、実装済みの全エンドポイント(登録・ログイン・ログアウト・自分の情報取得・ヘルスチェック・hello・todosのCRUD)がパス・メソッド単位で記載される。
2. **Given** 認証(登録/ログイン等)のリクエスト・レスポンス形式が既存のmarshmallowスキーマで定義されている、**When** 生成コマンドを実行する、**Then** それらのスキーマが`openapi.json`のコンポーネント定義として反映され、手書きの型定義と重複しない。

---

### User Story 2 - 開発者として実装とドキュメントの食い違いに気づける (Priority: P2)

開発者が、エンドポイントを変更したにもかかわらず`openapi.json`の再生成を忘れた場合に、それに気づける
手段がある(CI連携は別feature `007-ci-setup` に委譲するが、本feature側は「差分が出る」ことを保証する)。

**Why this priority**: 生成物が古いまま放置されると、`web`側の型生成が実装と食い違い、`006-openapi-generation`
自体の目的(手戻り防止)が達成できない。

**Independent Test**: 既存の`openapi.json`をコミットした状態から、エンドポイントの入出力を変更し、生成コマンドを
再実行して差分(`git diff`)が出ることを確認すれば、単独で価値を検証できる。

**Acceptance Scenarios**:

1. **Given** `openapi.json`がリポジトリにコミットされている、**When** エンドポイントの入出力形式を変更してから生成コマンドを再実行する、**Then** `openapi.json`に変更が反映され`git diff`で検知できる。

---

### Edge Cases

- 未実装のエンドポイント(`docs/design.md`の「画面別エンドポイント(検討中)」にある`posts`/`goals`/`events`等)は、コード自体が存在しないため`openapi.json`に含まれない。これは正しい挙動とする(実装済みの契約のみを反映する)。
- 生成コマンドを`dev`コンテナ以外(ホスト)で実行した場合、どう扱うか?(憲章 原則VI: devcontainer固定)
- 生成した`openapi.json`を手動で編集した場合、次回の再生成で上書きされ編集内容が失われる。これは意図した挙動とする(CONTRIBUTING.md §4: 生成物であり手動マージ禁止)。

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `api`は、実装済みの全エンドポイント(`/api/health`, `/api/hello`, `/api/register`, `/api/login`, `/api/logout`, `/api/me`, `/api/todos`のCRUD)を含むOpenAPIスキーマを生成できなければならない。
- **FR-002**: 生成されたスキーマは、既存のmarshmallowスキーマ(`RegisterSchema`, `LoginSchema`, `UserSchema`, `TodoSchema`)の内容(必須フィールド・型・バリデーション)を反映しなければならない。
- **FR-003**: 生成物は`openapi.json`としてリポジトリのルート直下に置かれ、コミットできなければならない(`docs/design.md` §3のディレクトリ構成に既に予約されている位置)。
- **FR-004**: 生成は開発者が1コマンドで実行できなければならない(`devcontainer`内)。
- **FR-005**: 生成されたスキーマは、各エンドポイントの認証要否(`@login_required`が付いているか)と、成功時・エラー時のレスポンス形式(`docs/design.md` §7の規約: 401/404/400 + `{"error": {...}}`)を記載しなければならない。
- **FR-006**: 生成コマンドは、コードを変更せずに何度実行しても同じ入力からは同じ出力を生成しなければならない(再実行可能性)。

### Key Entities

該当なし(本featureは新規の永続化データを持たない)。

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 実装済みの全エンドポイントが、1コマンドの実行結果として`openapi.json`に反映される。
- **SC-002**: エンドポイントの入出力を変更した場合、再生成によって`openapi.json`の差分が`git diff`で確認できる。
- **SC-003**: 開発者(フロントエンド担当)は、`openapi.json`を読むだけで、手書きのAPI型定義を作らずに済む。

## Assumptions

- 未実装のエンドポイント(掲示板・目標・タイムライン等)のスキーマ化は本featureの対象外とする(実装時に追って生成対象へ追加する)。
- `web`側での型生成コマンド自体(`openapi-typescript`等の導入)は`apps/web`の担当範囲であり、本featureの対象外とする(`docs/design.md` §13)。
- CIでの自動チェック(生成漏れの検知を自動化する)は別feature `007-ci-setup` に委譲する。
- 生成方式(コード内docstring方式か、専用の記述ファイル方式か等)の技術的な実現手段は`/speckit-plan`で決定する。
