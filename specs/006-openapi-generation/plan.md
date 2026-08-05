# Implementation Plan: openapi.jsonの生成

**Branch**: `006-openapi-generation` | **Date**: 2026-08-05 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/006-openapi-generation/spec.md`

## Summary

`apispec`(+ `apispec-webframeworks`のFlaskPlugin、`apispec.ext.marshmallow`のMarshmallowPlugin)を使い、
既存のBlueprint・View関数・marshmallow Schemaを変更せずにOpenAPI 3.0.3スキーマを生成する。各View関数の
docstringに軽量なYAMLを追記し、`apps/api/generate_openapi.py`を実行するとリポジトリルート直下の
`openapi.json`が生成・更新される。対象は実装済みエンドポイントのみ(health/hello/register/login/logout/me/todos)。

## Technical Context

**Language/Version**: Python 3.12(既存`apps/api`と同一)

**Primary Dependencies**: `apispec`, `apispec-webframeworks`(新規追加)。`marshmallow`は既存のものをそのまま使う。

**Storage**: 該当なし(生成にDB接続は不要)。

**Testing**: 生成後、`openapi.json`が妥当なJSONであること、対象エンドポイントが揃っていることを
`005-api-tests`と同様の考え方でpytestの軽量なテスト(`test_openapi_generation.py`)として確認する。
OpenAPI仕様そのものの厳密なバリデーション(`openapi-spec-validator`等の追加ツール導入)は本featureの
範囲外とする(YAGNI。今回のスコープでは構造の存在確認で十分)。

**Target Platform**: Linuxコンテナ(`dev`コンテナ内。憲章 原則VI)

**Project Type**: web-service(`apps/api`側)

**Performance Goals**: 該当なし

**Constraints**: 生成物`openapi.json`はリポジトリルート直下に置く(`docs/design.md` §3で予約済みの位置)。
生成は既存のBlueprint登録・ルーティングを変更しない。

**Scale/Scope**: 対象エンドポイントは7本(health, hello, register, login, logout, me, todos×5メソッド)。

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| 原則 | 該当ゲート | 判定 |
|---|---|---|
| V 契約駆動の境界 | `api`が`openapi.json`を生成してコミットする(本featureそのものがこのMUSTの実施)。依存追加(`apispec`, `apispec-webframeworks`)はバージョン固定で`requirements.txt`に追加する | PASS |
| I 規約は1箇所にのみ書く | 生成コマンドの実行方法は`apps/api/README.md`に追記する(他文書と重複させない) | PASS |
| VI devcontainer固定 | 生成・依存インストールは`dev`コンテナ内で行う | PASS |
| CI(2026-08-05決定) | 本featureはCIワークフロー自体を作らない(`007-ci-setup`に委譲)。生成漏れをCIで検知できるよう、1コマンドで再生成可能な状態にする | PASS |

違反・トレードオフの正当化が必要な項目なし。Complexity Trackingは記入不要。

### Post-Design 再評価(Phase 1完了後)

Phase 1の設計成果物を反映しても、既存ルート・既存Schemaへの破壊的変更は無い(docstring追記のみ)。
上表の全項目がPASS。

## Project Structure

### Documentation (this feature)

```text
specs/006-openapi-generation/
├── plan.md              # このファイル
├── research.md          # Phase 0 出力
├── data-model.md        # Phase 1 出力(該当なしを明記)
├── quickstart.md         # Phase 1 出力
└── tasks.md              # Phase 2 出力(/speckit-tasks が生成)
```

本featureは既存のAPI契約を生成するだけで新規の外部インターフェースを追加しないため、`contracts/`は
作成しない(生成物自体である`openapi.json`が契約である)。

### Source Code (repository root)

```text
apps/api/
├── requirements.txt          # apispec, apispec-webframeworks を追加
├── generate_openapi.py        # 新規: OpenAPIスキーマを生成しリポジトリルートへ書き出す
├── README.md                  # 「openapi.jsonの生成方法」節を追加
├── app/routes/
│   ├── health.py               # docstringにYAMLを追記(挙動は変更しない)
│   ├── hello.py                 # 同上
│   ├── auth.py                   # 同上(register/login/logout/me)
│   └── todos.py                   # 同上(list/get/create/update/delete)
└── tests/
    └── test_openapi_generation.py # 新規: 生成結果の構造を確認する軽量テスト

openapi.json                    # 新規: リポジトリルート直下(docs/design.md §3で予約済み)
```

**Structure Decision**: 既存のBlueprint・Schema定義には変更を加えず、docstring追記と新規スクリプト・
新規テストファイルの追加のみで完結させる。

## Complexity Tracking

*違反なしのため記入なし*
