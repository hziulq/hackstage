# Feature Specification: CI(Lint/テスト/openapi.json生成チェック)の整備

**Feature Branch**: `007-ci-setup`

**Created**: 2026-08-05

**Status**: Draft

**Input**: User description: "憲章(2026-08-05改定、v3.1.0)で『CIをPRに結果表示する。ただし必須ステータスチェックにはせずマージをブロックしない』方針が確定した。この方針に基づき、GitHub ActionsでLint・テスト(005-api-tests)・openapi.json生成差分(006-openapi-generation)のチェックを整備する。メンバーの開発経験が浅いため、CIに阻まれてpush・マージできない事態を避けることが最優先事項。"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 開発者としてPR上でLint・テストの結果を確認できる (Priority: P1)

開発者が、PRを作成した際に、手元で`pytest`やlintを実行し忘れていても、PR上でLintエラー・テスト失敗の
有無を確認できる。

**Why this priority**: リポジトリの評価対象にCI整備が含まれており、`005-api-tests`で整備した自動テストが
「実行されるだけ」で「PRで見える」状態になっていないと、変更のたびに手動で`pytest`を叩く手間が残る。

**Independent Test**: 意図的にLintエラーまたはテスト失敗を含むPRを作り、GitHub Actions上にその結果が
表示されることを確認すれば、単独で価値を検証できる。

**Acceptance Scenarios**:

1. **Given** PRが作成される、**When** GitHub Actionsが実行される、**Then** Lintとテストの結果(成功/失敗)がPR上のチェックとして表示される。
2. **Given** Lintエラーまたはテスト失敗を含むPRである、**When** マージを試みる、**Then** CIが赤くてもマージ自体は可能である(憲章「CI」節: 非ブロッキング)。

---

### User Story 2 - 開発者としてopenapi.jsonの生成漏れに気づける (Priority: P2)

開発者が、エンドポイントを変更したが`generate_openapi.py`の再実行を忘れた場合に、PR上でそれに気づける。

**Why this priority**: `006-openapi-generation`で「1コマンドで再生成できる」状態を作ったが、実際に
再生成し忘れるヒューマンエラーはCIで検知するのが最も確実。ただしP1(Lint/テストの可視化)より
影響範囲が狭いため優先度は下げる。

**Independent Test**: エンドポイントの入出力を変更してから`openapi.json`を再生成せずにPRを作り、
CI上で「生成物が古い」ことが分かる結果が出ることを確認すれば、単独で価値を検証できる。

**Acceptance Scenarios**:

1. **Given** `apps/api`のエンドポイントの入出力を変更した、**When** `openapi.json`を再生成せずにPRを作る、**Then** CI上で生成物と実装が食い違っていることが分かる結果が表示される。
2. **Given** 生成物が古いままである、**When** マージを試みる、**Then** マージ自体は可能である(非ブロッキング)。

---

### Edge Cases

- CIの実行に必要なデータベース(Postgres)は、GitHub Actions上でどう用意するか?(ローカルの`db`サービスと同等の環境が必要)
- 依存関係(`requirements.txt`)のインストールに失敗した場合、どのジョブがどう失敗として表示されるか?
- 同時に複数のPRが作られた場合、CIの同時実行数に制限はあるか(GitHub Actionsの既定の並列実行枠内で収まるか)?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: システムは、PRが作成・更新されるたびに自動でLintとテストを実行しなければならない。
- **FR-002**: システムは、Lint・テストの結果をPR上のチェックとして表示しなければならない(憲章「CI」節)。
- **FR-003**: システムは、`005-api-tests`で整備した`apps/api/tests/`のテストスイート全体を実行しなければならない。
- **FR-004**: システムは、`openapi.json`が現在の実装と一致しているか(再生成して差分が出ないか)を確認し、結果をPR上に表示しなければならない。
- **FR-005**: いずれのチェックも、失敗した場合にPRのマージを技術的に阻止してはならない(必須ステータスチェックにしない。憲章「CI」節)。
- **FR-006**: CIの実行環境は、ローカルの`dev`/`db`サービスと同等の前提(PostgreSQL、`apps/api`の依存関係)を用意しなければならない。

### Key Entities

該当なし。

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: PRを作成すると、追加の手動操作なしにLint・テスト・openapi.json生成チェックの結果がPR上に表示される。
- **SC-002**: Lintエラーやテスト失敗を含むPRでも、マージ操作自体はブロックされない。
- **SC-003**: `openapi.json`が実装と食い違っている状態のPRで、その食い違いがCIの結果から分かる。

## Assumptions

- Lintツールの選定(`ruff`等)は`/speckit-plan`で決定する(`.gitignore`に`.ruff_cache/`が既に用意されているため、`ruff`を第一候補とする)。
- CI基盤は`GitHub Actions`を前提とする(リポジトリがGitHub上にあるため。他のCI基盤の比較検討は本featureの対象外)。
- GitHub側のブランチ保護設定(必須ステータスチェックの有効/無効)自体の変更は、リポジトリのオーナーが必要に応じて行うものとし、本featureはワークフロー定義ファイルの追加までを範囲とする(現状ブランチ保護は未設定であり、追加のワークフローを「必須」にする設定変更を行わない限り、自動的に非ブロッキングの状態が保たれる)。
- `apps/web`側のLint/テストは`apps/web`の骨格が固まった時点で別途追加するものとし、本featureでは`apps/api`のみを対象とする。
