# Phase 1 Data Model: apiの自動テスト整備

本featureは新規の永続化エンティティを追加しない(既存の`User` / `Todo`モデルはそのまま)。
ここでは、テストコード内で作成する**一時的なテストデータ**の形だけを記録する。

## テスト内で作成するデータ

### テスト用利用者(User)

既存の`User`モデル(`apps/api/app/models/user.py`)をそのまま使う。テストごとに以下の値をユニークに指定して作成する。

| フィールド | 値の決め方 |
|---|---|
| `email` | テスト関数ごとに一意な値を明示的に指定する(例: `"login-success@example.com"`) |
| `password` | 固定のダミー文字列で良い(例: `"correct-horse"`) |
| `display_name` | 任意の固定文字列で良い |

### テスト用Todo

既存の`Todo`モデル(`apps/api/app/models/todo.py`)をそのまま使う。所有者分離テストでは、
異なる`User`に紐づく最低2件のTodoを作成する。

## ライフサイクル

すべてのテストデータは、research.mdで決定したSAVEPOINTベースのトランザクション内で作成され、
各テスト終了時にロールバックされる。テスト実行後、`users` / `todos`テーブルに新規データは残らない。
