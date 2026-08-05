# Phase 0 Research: ユーザー認証(ログイン・ログアウト)

## 1. パスワードハッシュ方式

- **Decision**: `argon2-cffi` を直接使う（`argon2.PasswordHasher`）。`User.set_password()` / `User.check_password()` として `app/auth/security.py` にラップする。
- **Rationale**: spec.mdの入力で明示的に「パスワードはargon2でハッシュ化」と指定されており、憲章 原則IVも argon2 または bcrypt を必須としている。`argon2-cffi` はメンテナンスが活発で、デフォルトパラメータがOWASP推奨に沿っている。
- **Alternatives considered**: `passlib`（argon2バックエンド経由でも良いが、近年メンテナンスが停滞気味で追加の抽象層が不要）、`bcrypt`（憲章上は許容されるが、spec.mdの明示的な指定と合わない）。

## 2. 認証フレームワーク

- **Decision**: `Flask-Login`。`extensions.py` に `login_manager = LoginManager()` を追加し、`User` に `UserMixin` を継承させる。
- **Rationale**: spec.mdの入力で明示。`docs/design.md` §8 で確定済みの「Flaskサーバーサイド署名付きCookieセッション」ともそのまま整合する。
- **Alternatives considered**: 独自セッション実装（Flask標準`session`を直接操作） — Flask-Loginは `current_user` / `@login_required` / `user_loader` など小規模チームが車輪の再発明をせずに済む標準的な薄いラッパーであり、採用しない理由がない。

## 3. レート制限

- **Decision**: `Flask-Limiter`。`POST /api/login` に `"5 per minute"`（送信元IPアドレスキー、`get_remote_address`）を適用。ストレージは既定の `memory://`（インメモリ）。
- **Rationale**: FR-009 / SC-004 で「短時間の連続試行を制限する」ことのみが要求されており、具体的な閾値はspecで未指定のため、ブルートフォース対策として一般的な値（1分あたり5回）を採用する。MVP規模でRenderの単一`pserv`インスタンス運用を想定しているため、インメモリストレージで十分。
- **既知のトレードオフ**: 本番は `gunicorn -w 4`（4ワーカープロセス）で起動するため、インメモリストレージはワーカーごとに独立し、レート制限は実質「ワーカー単位」でかかる（合計では設定値の最大4倍程度まで試行が通り得る）。ゼロにはならないため許容する。悪用が実際に問題化した場合はRedisバックエンドのストレージへの切り替えを検討する（憲章の「未決事項」と同様の先送り扱い）。
- **Alternatives considered**: Redisバックエンドを最初から使う — 現時点でRedisはインフラに存在せず、導入コストが見合わない。

## 4. 未ログイン時のレスポンス形式

- **Decision**: `LoginManager.unauthorized_handler` を上書きし、デフォルトのログイン画面へのリダイレクトではなく `{"error": {"code": "unauthorized", "message": "..."}}` + `401` をJSONで返す。
- **Rationale**: `docs/design.md` §7 で「未ログイン → 401」「入力エラー → `{"error": {...}}`」の形式が既に規約化されており、APIオンリーのバックエンドにリダイレクトは不適合。

## 5. 登録エンドポイントのパス

- **Decision**: `POST /api/register`。
- **Rationale**: spec.md FR-001 はオープン登録を必須要件としているが、`docs/design.md` §7 の認証系エンドポイント表には login/logout/me のみ記載されており登録エンドポイントが抜けている。既存の `/api/login` 等の命名規約に合わせ `/api/register` とする。
- **対応**: 憲章 原則I「設計値の変更は先に `docs/design.md` を更新する MUST」に従い、実装前に §7 の表へ追記する（本feature内のタスクとして実施）。

## 6. `todos.py` の暫定実装の解消

- **Decision**: `TodoSchema` から `user_id` フィールドを削除し、クライアントからの指定を受け付けない。`routes/todos.py` の全エンドポイントに `@login_required` を付与し、`request.args.get("user_id")` を `current_user.id` に置き換える。作成時は `Todo(user_id=current_user.id, ...)` とする。
- **Rationale**: `todos.py` / `schemas/todo.py` のコード内コメントに「Flask-Login未導入のための暫定実装。認証実装時にcurrent_user.idへ置き換える」と明記されており、本featureのスコープとして解消することがこの会話で確定済み。憲章 原則III（所有者確認はクエリ条件に含める、取得後のif判定は禁止）に完全準拠する既存パターンは変更不要で、`user_id`の取得元だけを差し替える。

## 未解決のNEEDS CLARIFICATION

なし。spec.mdのチェックリストで既に全項目解消済みであり、上記の実装方式選定で技術的な不明点も残っていない。
