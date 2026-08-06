# Implementation Plan: ユーザー認証(ログイン・ログアウト)

**Branch**: `003-user-auth` | **Date**: 2026-08-05 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/003-user-auth/spec.md`

## Summary

メール・パスワードによるオープン登録、ログイン、ログアウト、`/api/me` を Flask-Login + argon2 で実装する。
セッションは既存の `docs/design.md` §8 で確定済みの Cookie セッション方式（JWT不採用）にそのまま乗せる。
あわせて、認証未導入を理由に暫定実装だった `apps/api/app/routes/todos.py` / `app/schemas/todo.py` の
`user_id` クエリパラメータ方式を `current_user.id` に置き換える（コード内コメントで予告済みの対応）。

## Technical Context

**Language/Version**: Python 3.12（既存 `apps/api` と同一）

**Primary Dependencies**: Flask-Login（セッション/認証）, argon2-cffi（パスワードハッシュ）, Flask-Limiter（レート制限）。既存の Flask-SQLAlchemy / Flask-Migrate / marshmallow はそのまま利用。

**Storage**: PostgreSQL 17（既存）。`users` テーブルは既に `email`(unique) / `password_hash` / `display_name` を持っており、**新規マイグレーションは不要**。

**Testing**: 本feature単体では手動検証（quickstart.md の curl シナリオ）のみ行う。自動テストは別feature `005-api-tests` で整備する（この会話で確定済みの分割方針）。

**Target Platform**: Linux コンテナ（devcontainer / Render `pserv`）

**Project Type**: web-service（`apps/web` + `apps/api` の2アプリ構成のうち `apps/api` 側）

**Performance Goals**: SC-001（ログインから3秒以内に到達）を満たせば十分。特別なチューニングは不要。

**Constraints**: ログイン失敗時のレスポンスはメール存在有無を漏らさない一律文言・一律ステータス(401)にする(FR-008)。レート制限はログイン試行に対して必須(FR-009)。

**Scale/Scope**: MVPチーム規模（Render単一インスタンス想定）。水平スケールを前提にしたセッションストア設計は不要（憲章 原則VII: 署名付きCookieでプロセス内状態を持たない）。

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| 原則 | 該当ゲート | 判定 |
|---|---|---|
| III セキュリティ境界は api に一つだけ | 認証・認可判定は `api` のみ。所有者確認はクエリ条件(`filter_by(id=..., user_id=current_user.id)`)。権限なしは404、403は使わない。ログイン失敗は一律文言。レート制限必須 | PASS（設計に組込み） |
| IV 秘密情報をクライアントへ出さない | HttpOnly Cookie（既存 `config.py` で設定済み）。パスワードは argon2 でハッシュ。JWT不採用 | PASS |
| V 契約駆動の境界 | `openapi.json` の生成は別feature `006-openapi-generation` で対応（この会話で分割合意済み）。本featureでは `docs/design.md` §7 のエンドポイント表を更新し契約を文書化。依存バージョンは `requirements.txt` にピン留め | PASS（openapi.json生成は明示的に別feature委譲） |
| VI devcontainer固定 | 実装・依存インストールは `dev` コンテナ内で行う | PASS |
| I 規約は1箇所にのみ書く | `docs/design.md` §7 に `POST /api/register` が未記載（specにはあるが設計書に無いギャップ）。本featureで**先に** `docs/design.md` を更新してから実装する | PASS（Phase 1完了。Project Structureに `docs/design.md` 更新をタスクとして明記） |

違反・トレードオフの正当化が必要な項目なし。Complexity Trackingは記入不要。

### Post-Design 再評価（Phase 1完了後）

Phase 1の設計成果物（data-model.md / contracts / quickstart.md）を反映しても、新規マイグレーション・新規外部依存の追加による原則違反は無い。上表の全項目がPASS。

## Project Structure

### Documentation (this feature)

```text
specs/003-user-auth/
├── plan.md              # このファイル
├── research.md          # Phase 0 出力
├── data-model.md         # Phase 1 出力
├── quickstart.md         # Phase 1 出力
├── contracts/
│   └── auth-api.md       # Phase 1 出力
└── tasks.md              # Phase 2 出力（/speckit-tasks が生成）
```

### Source Code (repository root)

`docs/design.md` §3 で事前に固定されているディレクトリ構成にそのまま従う（`app/auth/` を認証・認可専用ディレクトリとして予約済み）。

```text
apps/api/
├── requirements.txt          # Flask-Login, argon2-cffi, Flask-Limiter を追加
└── app/
    ├── extensions.py         # login_manager, limiter を追加（db, migrate と同じ場所）
    ├── __init__.py           # init_app呼び出し、user_loader登録、unauthorized_handler、authブループリント登録
    ├── config.py              # 変更なし（SECRET_KEY, SESSION_COOKIE_* は既存のまま使う）
    ├── auth/                  # 新規: 認証・認可ロジック（design.mdで予約済みディレクトリ）
    │   ├── __init__.py
    │   └── security.py        # argon2 PasswordHasher のラップ（hash_password/verify_password）
    ├── models/
    │   └── user.py             # UserMixin継承、set_password/check_passwordメソッド追加
    ├── schemas/
    │   ├── user.py             # 新規: RegisterSchema, LoginSchema, UserSchema(出力用、password_hash除外)
    │   └── todo.py             # user_idフィールドを削除(サーバー側でcurrent_user.idを補う)
    └── routes/
        ├── auth.py             # 新規: POST /api/register, POST /api/login, POST /api/logout, GET /api/me
        └── todos.py            # user_idクエリパラメータを廃止しcurrent_user.idを使用、@login_required付与

docs/design.md                 # §7 認証系エンドポイント表に POST /api/register を追記
```

**Structure Decision**: 既存の `apps/api/app/{models,schemas,routes}` パターンをそのまま踏襲し、`docs/design.md` が既に予約している `app/auth/` を新設する。新規ファイルの追加のみで既存ディレクトリ構成の変更は無い。

## Complexity Tracking

*違反なしのため記入なし*
