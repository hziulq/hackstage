# Feature Specification: 掲示板・目標・カレンダーAPIの認証統合

**Feature Branch**: `010-secure-social-api`

**Created**: 2026-08-05

**Status**: Draft

**Input**: User description: "apps/api の掲示板・目標・カレンダー・リアクション関連の新規エンドポイント(008-auth-todo-apiブランチで追加、user_idをクライアントから受け取る暫定実装)に、既存の003-user-authと同じcurrent_user/@login_requiredベースの本物の認証を適用する。あわせて008-web-auth-openapi-types(ログイン/登録UI・openapi型生成)をpreviewに統合し、認証を追加した新エンドポイント分もopenapi.json・型生成に反映する。将来的にapiサービスをRenderのpserv(有料限定)から公開webサービス(無料枠あり)に切り替えられるようにするための安全性確保が目的。"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 開発者として掲示板・目標・カレンダーAPIをなりすまし不可能にする (Priority: P1)

開発者(バックエンド担当)が、`008-auth-todo-api`で追加された掲示板(`posts`)・目標(`goals`)・
カレンダー(`calendars`/`events`)・リアクション(`reactions`)のエンドポイントを、
クライアントが送る`user_id`を信用する暫定実装から、既存の`003-user-auth`と同じ
セッションベースの認証(`current_user`/`@login_required`)に置き換える。

**Why this priority**: 現状は誰でも任意の`user_id`を指定してリクエストを送れば他人になりすませる
状態であり、これを直さない限り`api`をRenderの`pserv`(常時有料)から公開`web`サービス
(無料枠あり)へ切り替える将来計画が実行できない。憲章上も認証は`003-user-auth`で
確立済みの前提があり、新規エンドポイントだけがそれに従っていないのは一貫性の欠如。

**Independent Test**: 未ログイン状態で保護対象のエンドポイントを呼ぶと401が返り、ログイン済みの
別ユーザーのIDを`user_id`として渡しても本人のデータとしてしか操作できないことを確認すれば、
単独で価値を検証できる。

**Acceptance Scenarios**:

1. **Given** 未ログイン状態、**When** `POST /api/goals`・`POST /api/posts`・`POST /api/reactions`等の
   保護対象エンドポイントを呼ぶ、**Then** 401が返り、データは作成されない。
2. **Given** ユーザーAとしてログイン済み、**When** リクエストの`user_id`にユーザーBのIDを指定して
   `PATCH /api/goals/{goal_id}/milestones/{milestone_id}`や`DELETE /api/goals/{goal_id}`を呼ぶ、
   **Then** サーバー側は`current_user.id`(ユーザーA)を正として扱い、リクエスト内の`user_id`は
   無視される(または不一致として拒否される)。
3. **Given** ユーザーAが作成した目標/投稿、**When** ユーザーBがそれを更新・削除しようとする、
   **Then** 403または404が返り、変更されない。

---

### User Story 2 - 開発者としてログイン/登録のWeb UIをpreviewに統合する (Priority: P2)

開発者が、`008-web-auth-openapi-types`で実装済みのログイン画面・登録画面・認証済みルートの
アクセス制御(`proxy.ts`)を`preview`に統合し、ユーザーが実際にブラウザから登録・ログイン・
ログアウトできる状態にする。

**Why this priority**: バックエンドの認証(`003-user-auth`)は既に存在するが、それを使う
フロントエンドのUIが`preview`に統合されておらず、ユーザーが実際に認証機能へ到達できない。

**Independent Test**: `preview`統合後、ブラウザで`/register`から新規登録し、`/login`でログインし、
認証必須ページ(`/timeline`等)にアクセスできること、未ログイン状態では`/login`にリダイレクトされる
ことを確認すれば、単独で価値を検証できる。

**Acceptance Scenarios**:

1. **Given** 未登録のユーザー、**When** `/register`でメールアドレス・表示名・パスワードを入力して
   送信する、**Then** アカウントが作成され`/login`に案内される(自動ログインはしない)。
2. **Given** 登録済みのユーザー、**When** `/login`で認証情報を入力する、**Then** セッションが確立し
   `/timeline`に遷移する。
3. **Given** 未ログイン状態、**When** `/timeline`・`/goals`・`/board`・`/mypage`にアクセスする、
   **Then** `/login`にリダイレクトされる。

---

### User Story 3 - 開発者として新規エンドポイントの契約をopenapi.json・型定義に反映する (Priority: P3)

開発者が、User Story 1で認証を追加した`posts`/`goals`/`calendars`/`events`/`reactions`の
エンドポイントを`openapi.json`に反映し、`apps/web`側の生成型(`api-types.generated.ts`)も
再生成して両者の食い違いを無くす。

**Why this priority**: `006-openapi-generation`の方針上、実装済みエンドポイントは契約として
`openapi.json`に反映されている必要がある。現状は`posts`/`goals`等が未反映のままで、
`api-types.generated.ts`にも存在しない(フロントから型安全に呼べない)。

**Independent Test**: 生成コマンドを再実行し、`openapi.json`に新エンドポイントが追加されること、
`apps/web`側の型生成コマンドを再実行して対応する型が`api-types.generated.ts`に追加されることを
確認すれば、単独で価値を検証できる。

**Acceptance Scenarios**:

1. **Given** User Story 1で認証を追加したエンドポイント一式、**When** `apps/api`の生成コマンドを
   実行する、**Then** `openapi.json`に該当パス・認証要否・レスポンス形式が追加される。
2. **Given** 更新された`openapi.json`、**When** `apps/web`の型生成コマンドを実行する、
   **Then** `api-types.generated.ts`に対応する型が追加され、既存の型(register/login/logout/me/todos)は
   変更されない。

---

### Edge Cases

- 掲示板(`/board`)ページは現状ローカルストレージのモックデータ(`useLocalStorageState`)で動作しており、
  今回認証を追加する`posts`等のAPIをまだ呼んでいない。本featureはAPI側の安全性確保と契約反映が範囲であり、
  `apps/web`の各画面をモックから実APIへ繋ぎ替える作業は別featureとする(Assumptions参照)。
- レート制限(`003-user-auth`の`/api/login`と同様の仕組み)を新規エンドポイントにも適用するかは、
  今回のスコープでは既存の`@login_required`パターンの適用のみとし、レート制限自体の追加は対象外とする。
- `calendars`の「メンバー一覧(スコアランキング)」(`GET /api/calendars/{id}/members`)は読み取り専用だが、
  当該カレンダーの参加者(`CalendarMember`)本人以外には見せない。非参加者・未ログインからのアクセスは
  403(または未ログインは401)を返す。

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `posts`・`goals`・`calendars`・`events`・`reactions`の各エンドポイントは、
  未ログイン状態からのアクセスに対して401を返さなければならない(`GET /api/calendars/{id}`等、
  読み取り専用で認証不要とすべきものは除く。対象範囲は`/speckit-plan`で確定する)。
- **FR-002**: データの作成・更新・削除を伴うエンドポイントは、リクエストボディ/クエリの`user_id`を
  信用してはならず、`current_user.id`(セッションから解決される本人のID)を正として扱わなければ
  ならない。
- **FR-003**: 本人以外が所有する目標・投稿・リアクションを更新・削除しようとした場合、
  403または404を返し、変更してはならない。
- **FR-004**: `008-web-auth-openapi-types`のログイン・登録画面・認証必須ルートのアクセス制御は、
  `003-user-auth`が提供する既存の`/api/register`・`/api/login`・`/api/logout`・`/api/me`と
  整合した形で`preview`に統合されなければならない。
- **FR-005**: FR-001〜FR-003で認証を適用したエンドポイントは、`openapi.json`に認証要否を含めて
  反映されなければならない(`006-openapi-generation`の既存方針に従う)。
- **FR-006**: `apps/web`側の生成型(`api-types.generated.ts`)は、更新後の`openapi.json`と
  食い違ってはならない。

### Key Entities

- **Post(投稿)**: 掲示板の質問。作成者(`user_id`→`current_user.id`)、タグ、カテゴリ、コメントを持つ。
- **Goal(目標)**: ユーザーの目標とマイルストーン。所有者本人のみ更新・削除できる。
- **Calendar / CalendarMember**: カレンダーとその参加者。参加者ごとのポイント集計(スコア)を持つ。
- **Event(予定)**: カレンダーに属する予定。非公開(`is_private`)な予定は本人のみ参照可能とする
  想定(現状は未実装、Edge Cases参照)。
- **Reaction**: 投稿等へのリアクション。作成者本人のみ削除できる。

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 未ログイン状態からの、保護対象エンドポイントへの作成・更新・削除リクエストは
  100%拒否される(401)。
- **SC-002**: 本人以外のユーザーIDを指定しても、他人のデータを作成・更新・削除できない
  (テストで検証可能)。
- **SC-003**: `preview`統合後、開発者がブラウザ操作のみで登録・ログイン・ログアウト・
  認証必須ページへの到達を一通り確認できる。
- **SC-004**: `openapi.json`と`apps/web`の生成型が、実装済みの全エンドポイントに対して
  食い違わない(生成コマンドを再実行しても差分が出ない)。

## Assumptions

- `008-auth-todo-api`ブランチのコード(ルート・スキーマ)はそのまま活用し、認証部分のみ
  `todos.py`と同じ`@login_required`パターンに置き換える。エンドポイントの入出力仕様
  (フィールド構成)自体の見直しは本featureの対象外とする。
- `apps/web`の各画面(`/board`・`/goals`等)を、モックデータ(`useLocalStorageState`)から
  今回契約反映したAPIへ実際に繋ぎ替える作業は本featureの対象外とする(別feature)。
- Renderの`api`サービスを`pserv`から公開`web`サービスへ実際に切り替える`render.yaml`の変更は
  本featureの対象外とする。本featureは「切り替えても安全な状態にする」ところまでを範囲とし、
  切り替え自体・追加のセキュリティレビューは別途判断する。
- レート制限・CSRF対策等、`003-user-auth`で確立済みの既存の仕組みを新規エンドポイントにも
  適用するかどうかは、`@login_required`の適用と表裏一体の範囲のみ対応し、新規の防御機構の
  追加は本featureの対象外とする。
