# Phase 1 Data Model: 掲示板・目標・カレンダーAPIの認証統合

本featureはDBスキーマ・マイグレーションを追加しない。以下は既存エンティティ
(`008-auth-todo-api`で確定済み)のうち、**「誰が値を設定するか」「誰が読めるか」が変わる**
フィールドのみを記録する。カラム定義自体は`apps/api/app/models/`を正とする。

## Post(投稿)

`apps/api/app/models/board.py`

| フィールド | 変更前 | 変更後 |
|---|---|---|
| `user_id` | クライアントが`PostSchema`経由で指定 | `current_user.id`をサーバー側で補う。`PostSchema.user_id`は`dump_only`化しクライアント指定を拒否 |

**読み取り制御**: `category`のみでの一覧(`anonymous_qa`/`prefecture_intern_info`)はログイン済みなら
制限なし。`calendar_id`を指定する場合(`timeline`投稿の`scope=group|personal`絞り込み)は
`current_user`が当該`calendar_id`の`CalendarMember`であることを確認する(research.md §6)。

## PostComment(投稿へのコメント)

`apps/api/app/models/board.py`

| フィールド | 変更前 | 変更後 |
|---|---|---|
| `user_id` | クライアントが`PostCommentSchema`経由で指定 | `current_user.id`をサーバー側で補う。`dump_only`化 |

**書き込み制御**: 対象`Post`が存在しない場合は404(既存のまま)。作成者本人以外の削除・更新API自体が
現状無いため所有者確認は不要(将来追加する場合は`todos.py`パターンに従う)。

## Goal(目標)

`apps/api/app/models/goal.py`

| フィールド | 変更前 | 変更後 |
|---|---|---|
| `user_id` | クライアントが`GoalSchema`/`GoalCreateSchema`経由で指定、一覧・削除はクエリパラメータ`user_id`で指定 | `current_user.id`をサーバー側で補う。スキーマの`user_id`は`dump_only`化。クエリパラメータ`user_id`は廃止し常に`current_user.id`を使う |

**読み取り・書き込み制御**: 一覧は`current_user.id`のGoalのみ。削除は
`Goal.query.filter(Goal.id == goal_id, Goal.user_id == current_user.id)`(既存パターンを
`current_user.id`に差し替えるのみ)。

## GoalMilestone(目標のマイルストーン)

`apps/api/app/models/goal.py`

所有者は`Goal.user_id`経由(直接の`user_id`カラムは持たない)。変更点:

| 項目 | 変更前 | 変更後 |
|---|---|---|
| 完了トグルの所有者確認 | クエリパラメータ`user_id`と`Goal.user_id`をJOIN条件で比較 | `current_user.id`と`Goal.user_id`をJOIN条件で比較(既存の`update_milestone`のJOINパターンはそのまま、`user_id`の取得元のみ変更) |

## Calendar / CalendarMember(カレンダーと参加者)

`apps/api/app/models/calendar.py`

カラム変更なし。**読み取り制御が新規に追加される**:

| エンドポイント | 変更前 | 変更後 |
|---|---|---|
| `GET /api/calendars/<id>` | 誰でも取得可能 | ログイン必須 + `current_user`が`CalendarMember`(`calendar_id=id`)であることを確認。非参加者・未参加は404 |
| `GET /api/calendars/<id>/members` | 誰でも取得可能 | 同上 |

判定ロジック: `CalendarMember.query.filter_by(calendar_id=calendar_id, user_id=current_user.id).first() is None` → 404。
`Calendar`自体の存在確認より前にこのチェックを行う(存在有無を漏らさないため、憲章 原則III)。

## Event(予定)

`apps/api/app/models/event.py`

| フィールド | 変更前 | 変更後 |
|---|---|---|
| `user_id` | クライアントが`EventSchema`経由で指定(作成エンドポイント自体は現状未実装、`list_events`のみ) | 将来の作成エンドポイント追加時は`current_user.id`を補う想定として`dump_only`化しておく |
| `is_private` | `list_events`でフィルタなし(全件返す) | `is_private=True`の予定は`user_id == current_user.id`のものだけ返す。`is_private=False`は`calendar_id`のメンバー全員に返す |

**読み取り制御**: `current_user`が`calendar_id`の`CalendarMember`であることを確認(非参加者は404)。
メンバーであっても他人の`is_private`な予定は結果から除外する(取得後のフィルタではなく
クエリ条件`or_(Event.is_private.is_(False), Event.user_id == current_user.id)`に含める)。

## Reaction(リアクション)

`apps/api/app/models/reaction.py`

| フィールド | 変更前 | 変更後 |
|---|---|---|
| `user_id` | クライアントが`ReactionSchema`経由で指定 | `current_user.id`をサーバー側で補う。`dump_only`化 |

**書き込み制御**: 削除は`Reaction.query.filter(Reaction.id == reaction_id, Reaction.user_id == current_user.id)`
(既存パターンを`current_user.id`に差し替えるのみ)。作成時の対象存在確認は既存のまま変更なし。

## 状態遷移

明示的なステートマシンは無し(既存エンティティのCRUD状態のみ)。認可判定はいずれも
リクエスト単位のクエリ条件で行われ、サーバー側でセッション以外の状態を持たない(憲章 原則VII)。
