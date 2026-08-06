# Phase 0 Research: 掲示板・目標・カレンダーAPIの認証統合

## 1. 前提ブランチの統合

- **Decision**: `origin/008-auth-todo-api`(routes/posts.py・goals.py・calendars.py・events.py・
  reactions.py・対応するschemas)と`origin/008-web-auth-openapi-types`(login/register画面・
  `proxy.ts`・`api-types.generated.ts`)を、`010-secure-social-api`ブランチへ`git merge`済み。
  両方とも`preview`未統合のリモートブランチで、`010-secure-social-api`の祖先ではなかった。
- **Rationale**: spec.mdのUser Story 1・Assumptionsは「`008-auth-todo-api`のコードをそのまま
  活用」を前提にしているが、実際のワーキングツリーには存在しなかった(調査で確認)。
  User Story 2も`008-web-auth-openapi-types`の`preview`統合そのものを範囲に含む。
  どちらも`git merge-tree`でコンフリクトが無いことを確認済みで、素直にマージする以外の
  選択肢(手動での再実装等)を取る理由がない。
- **Alternatives considered**: 該当コードを本featureで再実装する — 既に実装済みのコードが
  存在し重複実装は原則I(規約は1箇所にのみ書く)の精神に反する。採用しない。

## 2. 認可失敗時のステータスコード: 403 vs 404

- **Decision**: **404に統一する**。403は使わない。
- **Rationale**: 憲章 原則III(NON-NEGOTIABLE)「権限が無い場合は404を返すMUST。403は禁止
  (リソースの存在を漏らす)」、および`docs/design.md` §7「認証エラー: 未ログイン→401 /
  権限なし→404」が既に確定済みの規約。`todos.py`・`goals.py`(`update_milestone`/`delete_goal`)も
  この規約に従い既に404で実装されている。
- **spec.mdとの食い違いの解消**: spec.mdのAcceptance Scenario 3「403または404が返り」、
  Edge Cases「非参加者・未ログインからのアクセスは403(または未ログインは401)を返す」は
  憲章の404固定と矛盾する。憲章はGovernance節で「本憲章はプロジェクト内の他の慣習に優先する」
  と明記しており、spec.mdの記述より憲章を優先して404に一本化する。未ログインは401のまま変更なし。
- **Alternatives considered**: spec.mdの記述を優先して403を許容する — 憲章がNON-NEGOTIABLEと
  明記した原則に反するため採用しない。

## 3. 所有者確認パターン

- **Decision**: `todos.py`と同一のパターンを流用する。取得・更新・削除は
  `Model.query.filter_by(id=..., user_id=current_user.id).first()`のようにクエリ条件へ
  所有者確認を含め、`None`なら404。取得後に`if obj.user_id != current_user.id`で弾く実装はしない。
- **Rationale**: 憲章 原則III「認可は所有者確認をクエリ条件に含めるMUST」に明記された
  既定パターンであり、`todos.py`・`goals.py`(`update_milestone`)で実績がある。新規パターンの
  導入は不要。
- **Alternatives considered**: なし(憲章で唯一のパターンとして固定されている)。

## 4. `user_id`のスキーマ上の扱い

- **Decision**: `PostSchema`/`PostCommentSchema`/`GoalSchema`/`GoalCreateSchema`/`EventSchema`/
  `ReactionSchema`の`user_id`フィールドを`fields.Int(required=True)`から`fields.Int(dump_only=True)`
  に変更する(`TodoSchema`と同じ)。ルート側は`current_user.id`を明示的に渡してモデルを作成する。
- **Rationale**: `dump_only=True`にすることで、クライアントがペイロードに`user_id`を含めても
  `schema.load()`の結果(`data`)から自動的に除外される。`todos.py`の更新処理のように
  「`user_id`キーを個別にスキップする」分岐を毎エンドポイントに書く必要がなく、書き忘えのリスクを
  構造的に無くせる(憲章 原則IIIの「書き忘れが構造的に起きる実装は禁止」の精神に合致)。
- **Alternatives considered**: スキーマは変えずルート側で`payload.pop("user_id", None)`する
  (`todos.py`の更新処理と同方式) — `TodoSchema`自体は既に`dump_only`化されており一貫性が無い。
  新規追加分は`dump_only`パターンに統一する。

## 5. エンドポイント別の認証・認可スコープ(FR-001の対象範囲確定)

FR-001「読み取り専用で認証不要とすべきものは除く。対象範囲は`/speckit-plan`で確定する」を受けて
以下のように確定する。**本featureが解決すべき動機(`api`を将来公開`web`サービスへ切り替えても
安全にする)に基づき、`health`/`hello`/`register`/`login`以外は例外なくログイン必須とする。**

| エンドポイント | 認証 | 追加の認可 |
|---|---|---|
| `GET /api/posts` | ログイン必須 | `calendar_id`指定時は`current_user`が当該`Calendar`の`CalendarMember`であることを確認(§6参照)。それ以外(`category`のみでの一覧)は追加制限なし |
| `POST /api/posts` | ログイン必須 | `calendar_id`指定時は同上のメンバーシップ確認 |
| `POST /api/posts/<id>/comments` | ログイン必須 | 対象`Post`が存在しない場合404(既存のまま) |
| `GET /api/goals` | ログイン必須 | クエリパラメータ`user_id`は廃止。常に`current_user.id`のGoalのみ返す |
| `POST /api/goals` | ログイン必須 | なし |
| `PATCH /api/goals/<id>/milestones/<id>` | ログイン必須 | 所有者確認(既存の`filter_by`パターンを`current_user.id`に差し替え) |
| `DELETE /api/goals/<id>` | ログイン必須 | 所有者確認(同上) |
| `GET /api/events` | ログイン必須 | `calendar_id`のメンバーシップ確認 + `is_private`な予定は作成者本人以外に返さない(§6参照) |
| `POST /api/reactions` | ログイン必須 | なし(対象の存在確認のみ、既存のまま) |
| `DELETE /api/reactions/<id>` | ログイン必須 | 所有者確認(既存の`filter_by`パターンを`current_user.id`に差し替え) |
| `GET /api/calendars/<id>` | ログイン必須 | `current_user`が`CalendarMember`であることを確認、非参加者は404(spec.md Edge Cases) |
| `GET /api/calendars/<id>/members` | ログイン必須 | 同上 |

## 6. 追加で見つかった認可ギャップ(既存コードのレビューで判明)

- **`GET /api/posts?scope=personal&calendar_id=...`の漏洩リスク**: 現行実装は
  `Calendar.type == scope`のみを見て`calendar_id`が指定のカレンダーの`type`が`"personal"`かどうか
  しか確認しておらず、そのカレンダーが`current_user`自身のものかは確認していない。
  他人の個人カレンダーの`calendar_id`を知っていれば(あるいは総当たりされれば)閲覧できてしまう。
  → 本feature内で`calendar_id`が指定された場合は必ず`CalendarMember`による確認を追加する
  (spec.mdのFR-002「本人以外のデータを閲覧・操作できてはならない」という意図の範囲内の修正)。
- **`GET /api/events`の`is_private`未フィルタ**: `events.py`に既存コメント
  「TODO: 認証実装後、current_user.idを用いてis_privateな予定は本人以外に見せないよう絞り込みを
  追加する」があり、spec.md Key Entitiesの「非公開(`is_private`)な予定は本人のみ参照可能とする
  想定(現状は未実装)」と一致する。本feature内で解消する。

## 7. `openapi.json`生成への反映

- **Decision**: `apps/api/generate_openapi.py`の`spec.components.schema(...)`に
  `PostSchema`/`PostCommentSchema`/`GoalSchema`/`GoalMilestoneSchema`/`CalendarSchema`/
  `EventSchema`/`ReactionSchema`を追加し、`view_functions`リストに新規10エンドポイントを追加する。
  各ルート関数には`todos.py`と同じ形式(apispec向けYAMLブロックのdocstring、`security: - cookieAuth: []`)
  を追記する。
- **Rationale**: `006-openapi-generation`で確立済みの方式(実装済みビュー関数のdocstringから
  DB接続なしで生成)をそのまま踏襲する。新しい生成方式を導入する理由がない。

## 8. `apps/web`側の型再生成

- **Decision**: `openapi.json`再生成後に`apps/web`で`npm run generate:api-types`
  (`008-web-auth-openapi-types`で追加済みのスクリプト)を実行し、
  `apps/web/src/lib/api-types.generated.ts`を更新する。
- **Rationale**: 既存のスクリプトをそのまま使う。register/login/logout/me/todosの既存型を
  壊さないことをFR-006で要求されているため、生成後に既存型のフィールドが変わっていないことを
  quickstart.mdで確認する。

## 9. `docs/design.md`の記述ズレ

- **Decision**: `docs/design.md` §8「画面遷移の制御: web: `middleware.ts`」を
  `web: proxy.ts`に修正する。
- **Rationale**: `008-web-auth-openapi-types`の実装はNext.js 16([`PROXY_FILENAME`定数で確認済み](../../apps/web/node_modules/next/dist/lib/constants.js))
  の命名規則変更に従って`proxy.ts`を使っている。憲章 原則I「設計値の変更は先に`docs/design.md`を
  更新するMUST」に従い、実装(既にマージ済み)と文書の食い違いを本feature内で解消する。

## 10. 既存コードの軽微な不整合(参考、本featureのスコープ外の記録)

`008-auth-todo-api`ブランチ由来の`apps/api/app/routes/reactions.py`には
`from flask import Blueprint, jsonify, request`の重複import(1行目と3行目)がある。実害は無いが、
本feature内で`reactions.py`に`@login_required`等の変更を加える際に合わせて整理する
(`app/__init__.py`の同種の重複は統合直後に整理済み)。

## 未解決のNEEDS CLARIFICATION

なし。spec.mdのチェックリストで全項目解消済み、FR-001の対象範囲は上記§5で確定した。
