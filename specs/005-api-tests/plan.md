# Implementation Plan: apiの自動テスト整備

**Branch**: `005-api-tests` | **Date**: 2026-08-05 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/005-api-tests/spec.md`

## Summary

`apps/api`に`tests/`ディレクトリを新設し、`pytest`で認証(登録/ログイン/ログアウト/`/api/me`/レート制限)と
todos(認証必須化/所有者分離)の自動テストを整備する。既存の`db`サービス(開発用Postgres)をそのまま使い、
新規のテスト専用データベースは作らない。各テストをSAVEPOINTベースのトランザクションで囲みテスト後に
必ずロールバックすることで、開発用データを汚染せず(FR-007)、`compose.yaml`や環境変数の追加も不要にする。

## Technical Context

**Language/Version**: Python 3.12(既存`apps/api`と同一)

**Primary Dependencies**: `pytest`(新規追加)。既存の Flask / Flask-SQLAlchemy / Flask-Login / Flask-Limiter /
marshmallow はそのまま利用し、テスト用の追加ライブラリ(factory-boy 等)は導入しない(YAGNI。テスト対象が
小規模で、素の fixture で十分)。

**Storage**: PostgreSQL 17(既存の`db`サービス)。新規マイグレーション無し。テスト専用データベースは作らず、
既存の開発用データベースにSAVEPOINTトランザクションで接続し、テスト終了時にロールバックする。

**Testing**: `pytest`。`apps/api`ディレクトリで`python -m pytest`を実行する。テストはFlaskの`app.test_client()`
経由でアプリを直接呼び出す(ネットワーク越しの`api`コンテナへのcurlではない)。`dev`コンテナは既に`db`サービスへの
接続情報(`DATABASE_URL`)と`003-user-auth`で入れた依存(Flask-Login等)を持っているため、追加のコンテナ起動は不要。

**Target Platform**: Linuxコンテナ(`dev`コンテナ内。憲章 原則VI)

**Project Type**: web-service(`apps/api`側のみ。既存の単一プロジェクト構成にtests/を追加)

**Performance Goals**: 該当なし(テストスイート自体の実行速度に特別な目標は設けない。SC-004の「1コマンドで実行・結果確認できる」を満たせば十分)

**Constraints**: レート制限(`Flask-Limiter`のインメモリストレージ)がテスト間で状態を共有しないよう、各テスト前に
ストレージをリセットする(Edge Caseで指摘した相互干渉を防ぐ)。

**Scale/Scope**: 認証エンドポイント5本(register/login/logout/me、レート制限込み) + todos CRUD 5本(list/get/create/update/delete)を対象にする。フロントエンド(`apps/web`)は対象外。

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| 原則 | 該当ゲート | 判定 |
|---|---|---|
| I 規約は1箇所にのみ書く | テストの実行手順は`docs/design.md`や憲章に既存の記述が無い新規手順のため、`README.md`(`apps/api/README.md`)に追記する。他文書と重複させない | PASS |
| V 契約駆動の境界 | 依存追加(`pytest`)は`requirements.txt`にバージョン固定でコミットする。SQLは既存ORM経由のみで新規の生SQLは書かない | PASS |
| VI devcontainer固定 | テスト実行は`dev`コンテナ内でのみ行う。ホスト側での`pytest`実行は想定しない | PASS |
| CI(2026-08-05決定) | 本featureはCIワークフロー自体を作らない(`007-ci-setup`に委譲)。ただしCIが`pytest`を実行できる状態(1コマンドで実行可能)にしておく必要がある(FR-009) | PASS(前提を満たす設計) |

違反・トレードオフの正当化が必要な項目なし。Complexity Trackingは記入不要。

### Post-Design 再評価(Phase 1完了後)

Phase 1の設計成果物を反映しても、新規マイグレーション・新規の重い依存追加(factory-boy等の導入)は無い。
上表の全項目がPASS。

## Project Structure

### Documentation (this feature)

```text
specs/005-api-tests/
├── plan.md              # このファイル
├── research.md          # Phase 0 出力
├── data-model.md        # Phase 1 出力
├── quickstart.md        # Phase 1 出力
└── tasks.md              # Phase 2 出力(/speckit-tasks が生成)
```

本featureは新規の外部インターフェース(API契約)を追加しないため、`contracts/`は作成しない。

### Source Code (repository root)

```text
apps/api/
├── requirements.txt        # pytest を追加
├── pytest.ini               # testpaths=tests、必要な最小設定のみ
├── README.md                 # 「テストの実行方法」節を追加
└── tests/
    ├── conftest.py            # app fixture、SAVEPOINTトランザクションfixture、
    │                          # limiterストレージリセットfixture、テスト用ユーザー作成ヘルパー
    ├── test_auth.py            # 登録/重複登録/ログイン成功/ログイン失敗一律エラー/ログアウト/me
    ├── test_auth_rate_limit.py # レート制限(429)
    └── test_todos.py           # 未ログイン401、所有者分離(自分のtodoのみ操作可能)
```

**Structure Decision**: 既存の`apps/api/`直下に`tests/`を新設する(spec.mdのKey Entitiesで定めた通り)。
Flaskアプリのapp factory(`create_app()`)はそのまま使い、変更しない。レート制限テストのみ他のテストと
干渉しやすいため別ファイル(`test_auth_rate_limit.py`)に分離する。

## Complexity Tracking

*違反なしのため記入なし*
