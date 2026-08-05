# Implementation Plan: CI(Lint/テスト/openapi.json生成チェック)の整備

**Branch**: `007-ci-setup` | **Date**: 2026-08-05 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/007-ci-setup/spec.md`

## Summary

GitHub Actionsで`apps/api`向けのCIワークフロー(`.github/workflows/api-ci.yml`)を新規作成する。
`ruff`によるLint、`postgres:17`サービスコンテナ上での`pytest`(`005-api-tests`)、
`generate_openapi.py`の再実行による`openapi.json`生成差分チェック(`006-openapi-generation`)の
3ジョブ構成にする。いずれも失敗してもワークフロー全体・PRのマージ自体はブロックしない
(憲章「CI」節、v3.1.0)。

## Technical Context

**Language/Version**: Python 3.12(既存`apps/api`と同一)。CIランナーは`ubuntu-latest`。

**Primary Dependencies**: `ruff`(新規追加、CI専用。`apps/api/requirements.txt`には追加せず、
ワークフロー内で直接`pip install ruff`する。理由はConstitution Check参照)。

**Storage**: `postgres:17`(GitHub Actionsの`services`。ローカルの`compose.yaml`の`db`サービスと
同じイメージバージョン)。

**Testing**: `pytest`(既存の`apps/api/tests/`をそのまま実行する。新規テストは追加しない)。

**Target Platform**: GitHub Actions(`ubuntu-latest`)。

**Project Type**: CI設定(コード変更ではなく`.github/workflows/`の追加)。

**Performance Goals**: 該当なし。

**Constraints**: いずれのジョブ・ステップも、失敗時にワークフロー全体を失敗させ**ない**(FR-005)。
Secretsは使わない(CI用のダミー値で十分。本番の資格情報は関係しない)。

**Scale/Scope**: `apps/api`のみ。`apps/web`は対象外(spec.mdのAssumptions)。

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| 原則 | 該当ゲート | 判定 |
|---|---|---|
| CI(2026-08-05決定、v3.1.0) | PRにLint/テスト/openapi.json生成差分の結果を表示するMUST。必須ステータスチェックにしないMUST。本featureがこのMUSTの実施そのもの | PASS |
| V 契約駆動の境界 | `apps/api/requirements.txt`に追加する依存は無い(`ruff`はCIワークフロー内のみで使い、アプリケーションの実行に必須ではないためrequirements.txtに含めない)。既存の`005-api-tests`/`006-openapi-generation`をそのまま利用する | PASS(依存の新規追加なし) |
| VI devcontainer固定 | 本featureが対象とするのはGitHub Actionsの実行環境であり、`dev`コンテナの話ではない。ローカルでの動作確認(ワークフローファイルのYAML構文・ロジックの妥当性)は`dev`コンテナ内で行う | PASS |
| I 規約は1箇所にのみ書く | ワークフローの内容は`.github/workflows/api-ci.yml`のみに書く。`CONTRIBUTING.md`の既存の「CI」節(007-ci-setupで追加、と予告済み)は既に存在するため重複追記しない | PASS |

違反・トレードオフの正当化が必要な項目なし。Complexity Trackingは記入不要。

### Post-Design 再評価(Phase 1完了後)

Phase 1の設計成果物を反映しても、アプリケーションコード側の依存追加・破壊的変更は無い(ワークフロー
ファイルの追加のみ)。上表の全項目がPASS。

## Project Structure

### Documentation (this feature)

```text
specs/007-ci-setup/
├── plan.md              # このファイル
├── research.md          # Phase 0 出力
├── data-model.md        # Phase 1 出力(該当なしを明記)
├── quickstart.md         # Phase 1 出力
└── tasks.md              # Phase 2 出力(/speckit-tasks が生成)
```

本featureはAPI契約を追加しないため`contracts/`は作成しない。

### Source Code (repository root)

```text
.github/
└── workflows/
    └── api-ci.yml         # 新規: lint / test / openapi-check の3ジョブ

apps/api/pyproject.toml      # 新規: ruffの対象パス設定のみ(最小構成)
```

**Structure Decision**: `.github/workflows/`を新規作成する以外、既存コードへの変更は無い。
`apps/api/pyproject.toml`は`ruff`の対象ディレクトリ指定のためだけに追加する最小構成。

## Complexity Tracking

*違反なしのため記入なし*
