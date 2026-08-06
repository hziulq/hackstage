# Phase 1 Data Model: グループカレンダーの作成・共有と予定作成

本featureはDBスキーマ・マイグレーションを追加しない。既存エンティティ(`calendars`/
`calendar_members`/`events`、`008-auth-todo-api`・`010-secure-social-api`で確定済み)の
うち、**初めて実際に書き込まれる・読み書きの主体が変わる**フィールドのみを記録する。

## Calendar(カレンダー)

`apps/api/app/models/calendar.py`(カラム変更なし)

| フィールド | 変更前 | 変更後 |
|---|---|---|
| `type` | `"personal"`のみ実際に作成されていた(`010`の`get_my_personal_calendar`) | `"group"`も`POST /api/calendars`で作成されるようになる |
| `invite_code` | 常に`NULL`(発行経路が無かった) | グループカレンダー作成時に`secrets.token_urlsafe(6)`で発行し、`UNIQUE`制約のまま利用する |
| `owner_id` | 個人カレンダーのみ | グループカレンダー作成者も同様に設定 |

## CalendarMember(カレンダー参加者)

`apps/api/app/models/calendar.py`(カラム変更なし)

| フィールド | 変更前 | 変更後 |
|---|---|---|
| 作成経路 | `get_my_personal_calendar`が作成者を`role="owner"`で登録するのみ | グループ作成時も同様に`role="owner"`で登録。招待コード参加時は`role="member"`で登録 |

**冪等性**: `UniqueConstraint(calendar_id, user_id)`(既存)により、同一利用者が同じグループに
二重登録されることはDB制約でも防止される。アプリ側でも参加済みかを事前確認し、既存レコードが
あれば新規作成しない(FR-005)。

## Event(予定)

`apps/api/app/models/event.py`(カラム変更なし)。`EventSchema`も`010`時点で
`calendar_id`必須・`user_id`は`dump_only`になっており変更不要。

| フィールド | 変更前 | 変更後 |
|---|---|---|
| 作成経路 | 存在しない(`GET /api/events`の一覧取得のみ) | `POST /api/events`で作成可能になる。`current_user.id`をサーバー側で補う |

**書き込み制御**: `current_user`が`calendar_id`の`CalendarMember`であることを`is_calendar_member()`
(`010`で追加済みの共通ヘルパー)で確認する。非参加者からの作成は404。

**読み取り制御**: 変更なし(`010`で確立済みの`is_private`フィルタをそのまま使う)。

## 新規スキーマ(`apps/api/app/schemas/calendar.py`)

| スキーマ | 用途 | フィールド |
|---|---|---|
| `CalendarCreateSchema` | `POST /api/calendars`の入力 | `name`(必須、1〜100文字) |
| `CalendarJoinSchema` | `POST /api/calendars/join`の入力 | `invite_code`(必須、1〜32文字) |

出力は既存の`CalendarSchema`(全フィールド`dump_only`)をそのまま使う。

## 状態遷移

- **Calendar**: 作成時点で`type`が確定し、以後変更されない(グループ⇄個人の切り替えは無い)。
- **CalendarMember**: 「参加していない」→「参加済み(owner または member)」の一方向。脱退は
  本featureの対象外(Assumptions)。
- **Event**: 作成のみ(更新・削除は本featureの対象外)。

## 既知の制約(research.md §6)

「自分が参加しているグループカレンダーの一覧」を返すエンドポイントは無い。`apps/web`は
グループ作成・参加時のレスポンスに含まれる`calendar_id`をブラウザのlocalStorageに保持して
以後利用する(`GET /api/calendars/mine`が個人カレンダー用に持つ「自分の」という概念の、
グループカレンダー版に相当するエンドポイントは今回追加しない)。別ブラウザ・別デバイスからは
再取得できない制約が残ることを許容する(Assumptions参照、将来必要になれば一覧エンドポイントを
追加検討する)。
