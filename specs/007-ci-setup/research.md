# Phase 0 Research: CI(Lint/テスト/openapi.json生成チェック)の整備

## 1. CI基盤

- **Decision**: GitHub Actions。`.github/workflows/api-ci.yml`を新規作成する。
- **Rationale**: リポジトリがGitHub上にあり、追加の外部サービス連携やアカウント作成が不要。憲章「CI」節で名指しされている(「GitHub Actions等」)。

## 2. Lintツール

- **Decision**: `ruff`。
- **Rationale**: `.gitignore`に既に`.ruff_cache/`が用意されており(初期化時点で想定済み)、Python向けの単一ツールでlint(flake8相当)を高速に実行できる。設定ファイルは追加せず既定のルールセットで開始する(YAGNI。厳しすぎるルールで経験の浅いメンバーがCIに阻まれることを避ける方針(spec.mdのAssumptions)と、まず動く状態を優先する)。
- **Alternatives considered**: `flake8` + `black`の組み合わせ — 複数ツールの管理が増え、単一の`ruff`で代替できる範囲。

## 3. テスト実行環境(DB)

- **Decision**: GitHub Actionsの`services`機能で`postgres:17`コンテナを起動し、`005-api-tests`の`apps/api/tests/`を`postgres`サービスに対して実行する。`DATABASE_URL`・`SECRET_KEY`はワークフロー内の環境変数として設定する(リポジトリのSecretsは使わない。値はローカル開発用の`.env.example`と同様に、CI専用のダミー値で構わない)。
- **Rationale**: `compose.yaml`の`db`サービス(`postgres:17`)と同じイメージを使うことで、ローカルとCIの挙動差を減らす(憲章 原則VI相当の考え方を、devcontainer前提が無いCI環境にも適用する)。`005-api-tests`のテストはSAVEPOINTロールバックで自己完結しており、CI上でも同じ`db_session`fixtureがそのまま使える。

## 4. openapi.json生成差分チェックの実現方法

- **Decision**: CIのジョブ内で`python generate_openapi.py`を実行した後、`git diff --exit-code openapi.json`を実行する。差分があれば当該ステップは失敗(赤)になるが、ジョブ自体・ワークフロー全体は成功として終了させる(`continue-on-error: true`をこのステップにのみ付与し、後続ステップでその結果をサマリに出す)。
- **Rationale**: FR-004(結果をPR上に表示する)とFR-005(マージを阻止しない)を同時に満たす。ステップ単位で`continue-on-error: true`を使えば、GitHub Actions UI上は該当ステップが⚠️マーク付きで「失敗したが続行」として視覚的に区別され、ジョブ全体の成否(≒チェックの成否)には影響しない。

## 5. 非ブロッキング(必須ステータスチェックにしない)の実現方法

- **Decision**: ワークフロー定義ファイル自体では何もしない(GitHub Actionsのワークフローは、GitHubのブランチ保護設定で「必須」に指定されない限り、既定でマージをブロックしない)。本feature範囲はワークフロー定義の追加までとし、ブランチ保護設定(GitHubのリポジトリ設定)の変更は行わない。
- **Rationale**: 現状このリポジトリにブランチ保護は設定されていない(`main`への直接pushが技術的に禁止されていない)。ブランチ保護のON/OFFはワークフローファイルの外側にあるリポジトリ設定であり、憲章の遵守レビュー手続き(統治手続きの変更は専用PR・オーナー承認)の対象になり得る。本featureでは「設定変更をしない」ことそのものが非ブロッキング原則の遵守であり、追加でリポジトリ設定を変更する行為は行わない。

## 6. Lint対象・テスト対象の範囲

- **Decision**: `apps/api`のみを対象にする。`apps/web`はLint/テストの土台がまだ無いため対象外(spec.mdのAssumptions)。
- **Rationale**: `apps/web`用のワークフローを本featureで作ると、まだ固まっていない`apps/web`の骨格に対して「何を検証するか」を決め打ちすることになり、YAGNI違反になる。`apps/web`の骨格が固まった時点で別途追加する。

## 未解決のNEEDS CLARIFICATION

なし。
