# API Contract: 掲示板・目標・カレンダー・リアクション系エンドポイント

`docs/design.md` §7の規約(パス接頭辞`/api/`、JSON、成功時はエンベロープなし、
入力エラーは`400 {"error": {"code","message","fields"}}`、未ログインは`401`、
**権限なしは`404`固定**(`403`は使わない、憲章 原則III・research.md §2))に従う。

以下は認証統合後の契約。フィールド構成自体(リクエスト/レスポンスのボディ形状)は
`008-auth-todo-api`時点のものを変更しない。変更点は**認証要否と`user_id`の扱いのみ**。

## GET /api/posts

一覧取得(`category`/`tag`/`prefecture_id`/`calendar_id`/`scope`でフィルタ)。

- **認証**: ログイン必須。未ログインは`401`。
- **認可**: `calendar_id`を指定する場合、`current_user`が当該カレンダーの`CalendarMember`で
  なければ`404`(存在有無を漏らさない)。`calendar_id`未指定(`category`のみでの一覧)は
  ログイン済みであれば追加制限なし。
- **レスポンス**: 変更なし(`anonymous_qa`カテゴリは`user_id`を`null`にする匿名化は既存のまま維持)。

## POST /api/posts

新規投稿。

- **認証**: ログイン必須。
- **認可**: `user_id`はリクエストボディで指定不可(`PostSchema.user_id`は`dump_only`)。
  常に`current_user.id`で作成する。`calendar_id`指定時は上記と同じメンバーシップ確認。
- **レスポンス**: 変更なし。

## POST /api/posts/{post_id}/comments

コメント追加。

- **認証**: ログイン必須。
- **認可**: `user_id`はリクエストボディで指定不可、`current_user.id`で作成する。
  対象`post_id`が存在しない場合は`404`(既存のまま)。

## GET /api/goals

自分の目標一覧。

- **認証**: ログイン必須。
- **認可**: クエリパラメータ`user_id`は**廃止**。常に`current_user.id`のGoalのみ返す
  (他ユーザーの目標を`user_id`指定で覗く手段自体を無くす)。

## POST /api/goals

新規目標作成(マイルストーン自動生成込み)。

- **認証**: ログイン必須。
- **認可**: `user_id`はリクエストボディで指定不可、`current_user.id`で作成する。

## PATCH /api/goals/{goal_id}/milestones/{milestone_id}

マイルストーン完了トグル。

- **認証**: ログイン必須。
- **認可**: クエリパラメータ`user_id`は廃止。`Goal.user_id == current_user.id`を
  JOIN条件に含めて所有者確認(既存の`update_milestone`の実装パターンを流用)。
  存在しない、または他人のマイルストーンは`404`。

## DELETE /api/goals/{goal_id}

目標削除。

- **認証**: ログイン必須。
- **認可**: クエリパラメータ`user_id`は廃止。`Goal.query.filter(id=goal_id, user_id=current_user.id)`。
  他人の目標は`404`。

## GET /api/events

予定一覧(`calendar_id`必須)。

- **認証**: ログイン必須。
- **認可**: `current_user`が`calendar_id`の`CalendarMember`でなければ`404`。
  メンバーであっても、他人が作成した`is_private=true`の予定は結果に含まれない
  (`is_private=false`または`user_id == current_user.id`のみクエリ条件で返す)。

## POST /api/reactions

リアクション追加(既存: 同一対象への重複は`kind`を上書き)。

- **認証**: ログイン必須。
- **認可**: `user_id`はリクエストボディで指定不可、`current_user.id`で作成/更新する。
  対象(`event`/`post`)が存在しない場合は`404`(既存のまま)。

## DELETE /api/reactions/{reaction_id}

リアクション削除。

- **認証**: ログイン必須。
- **認可**: クエリパラメータ`user_id`は廃止。`Reaction.query.filter(id=reaction_id, user_id=current_user.id)`。
  他人のリアクションは`404`。

## GET /api/calendars/{calendar_id}

カレンダー基本情報(グループ名・招待コード)。

- **認証**: ログイン必須(**変更**: 従来は未認証で誰でも取得可能だった)。
- **認可**: `current_user`が`CalendarMember`でなければ`404`(spec.md Edge Cases)。

## GET /api/calendars/{calendar_id}/members

参加者一覧(スコアランキング)。

- **認証**: ログイン必須(**変更**: 従来は未認証で誰でも取得可能だった)。
- **認可**: `current_user`が`CalendarMember`でなければ`404`。

## 共通の副作用

- 上記全エンドポイントに`security: - cookieAuth: []`を`generate_openapi.py`が拾えるdocstring
  (apispec形式)で明記し、`openapi.json`に反映する(research.md §7)。
- `apps/web/src/lib/api-types.generated.ts`を`npm run generate:api-types`で再生成する
  (research.md §8)。既存のregister/login/logout/me/todosの型は変更されない(FR-006)。
