# Phase 1 Data Model: ユーザー認証(ログイン・ログアウト)

## User（既存エンティティ。カラム変更・マイグレーション追加なし）

`apps/api/app/models/user.py` に定義済み。

| フィールド | 型 | 制約 | 用途 |
|---|---|---|---|
| `id` | Integer | PK | ユーザー識別子。他モデルの `user_id` FKの参照先 |
| `email` | String(255) | unique, not null | ログインID。重複登録拒否(FR-002)の対象 |
| `password_hash` | String(255) | not null | argon2ハッシュ文字列を格納（既存カラムをそのまま利用。argon2出力は通常100文字未満で255に収まる） |
| `display_name` | String(100) | not null | `/api/me` レスポンスに含む表示名 |
| `avatar_url` | String(500) | nullable | `/api/me` レスポンスに含む（既存カラム。本feature内では設定手段を追加しない） |

### 本feature内で追加する振る舞い（マイグレーション不要、モデルクラスへのメソッド追加のみ）

- `UserMixin`（Flask-Login）を継承し、`current_user` / `is_authenticated` 等を利用可能にする。
- `set_password(raw_password: str) -> None`: `app/auth/security.py` の `hash_password()` を呼び argon2 ハッシュを `password_hash` に設定する。
- `check_password(raw_password: str) -> bool`: `app/auth/security.py` の `verify_password()` を呼び検証する。

### バリデーションルール（`app/schemas/user.py` で表現）

- `email`: 必須、メール形式（marshmallowの `validate.Email()`）
- `password`: 必須、最小長8文字（specに明示的な下限は無いため、脆弱すぎない一般的な値として採用。将来強度要件が出た場合は別途仕様化）
- `display_name`: 必須、1〜100文字（既存カラム長に合わせる）

### 出力スキーマ（`UserSchema`, `/api/me` 用）

`password_hash` は**含めない**（憲章 原則IV: 秘密情報をクライアントへ出さない）。

| フィールド | 出力有無 |
|---|---|
| `id` | ○ |
| `email` | ○ |
| `display_name` | ○ |
| `avatar_url` | ○ |
| `password_hash` | ✗ 常に除外 |

## Todo（既存エンティティ。所有者取得方法のみ変更）

`user_id` フィールドはモデル・DBスキーマとして変更なし。変わるのは「誰が値を設定するか」のみ:

- **変更前**: クライアントがリクエストの `user_id`（クエリパラメータ or ボディ）で指定
- **変更後**: サーバーが `current_user.id` から補う。クライアントからの `user_id` 指定は `TodoSchema` から削除し受け付けない

## 状態遷移

認証まわりに明示的なステートマシンは無い（ログイン/ログアウトはCookieセッションの有無のみで表現される。憲章 原則VII: サーバー側にプロセス内状態を持たない）。
