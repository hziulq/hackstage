# Implementation Plan: Renderへのデプロイ準備(render.yaml / web Dockerfile / healthz)

**Branch**: `008-render-deploy-prep` | **Date**: 2026-08-05 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/008-render-deploy-prep/spec.md`

## Summary

`docs/design.md` §11で値まで決まっているRender Blueprint(`render.yaml`)を新規作成し、
`web`(`type: web`, `docker`, `dockerTarget: prod`)・`api`(`type: pserv`, 既存Dockerfileをそのまま使用)・
`db`(Postgres 17、`fromDatabase`で`api`へ注入)の3サービスを定義する。合わせて、`apps/web`に
不足している`Dockerfile`(dev/prodマルチステージ、`output: "standalone"`)と`/healthz`
Route Handlerを追加する。Renderダッシュボード上でのサービス作成・接続・秘密値入力は
このfeatureの範囲外(ユーザー自身が行う)。

## Technical Context

**Language/Version**: TypeScript/Node 22 LTS(`apps/web`)。YAML(`render.yaml`)。既存の
`apps/api`(Python 3.12)は無変更。

**Primary Dependencies**: 新規の実行時依存追加は無い。`apps/web/next.config.js`に
`output: "standalone"`を追加する(Next.js本体が既に提供する機能。追加パッケージ不要)。

**Storage**: Render管理のPostgres 17(`render.yaml`の`databases:`)。ローカルの`compose.yaml`の
`db`(`postgres:17`)と一致させる。

**Testing**: 手動確認(`quickstart.md`)。`docker build --target prod` / `--target dev`の
ビルド成功と`/healthz`の200応答をローカルで確認する。自動テストの追加は本feature範囲外
(`render.yaml`・Dockerfileはテスト対象というより構成ファイルであるため)。

**Target Platform**: Render(`web`: Web Service / `api`: Private Service / `db`: マネージドPostgres)。
ローカル確認は`dev`コンテナ内の`docker build`/`docker run`。

**Project Type**: インフラ構成ファイルの追加(Web application: `apps/web`への最小限のコード追加を含む)。

**Performance Goals**: 該当なし。

**Constraints**: `render.yaml`に秘密値を書かない(憲章 原則IV、FR-002)。`dev`サービスを
`render.yaml`に含めない(FR-003)。`apps/web`に`app/api/**/route.ts`を作らない(憲章 原則II。
`/healthz`は`/api/`の外なので抵触しない)。

**Scale/Scope**: `render.yaml`本体、`apps/web/Dockerfile`、`apps/web/.dockerignore`、
`apps/web/src/app/healthz/route.ts`、`apps/web/next.config.js`(`output`追加のみ)。
`apps/api`・既存の`apps/web`の画面コードは変更しない。

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| 原則 | 該当ゲート | 判定 |
|---|---|---|
| I 規約は1箇所にのみ書く | `render.yaml`は`docs/design.md` §11の値をそのまま実装するのみで、値そのものを他文書に再定義しない | PASS |
| II 単一公開オリジン | `/healthz`は`/api/`配下ではない唯一の例外(design.md §6で明記)。`app/api/**/route.ts`は追加しない | PASS |
| III セキュリティ境界はapiに一つだけ | `/healthz`は認証・認可判定を行わない(単純な起動確認のみ)。既存の認証境界に変更なし | PASS(該当機能なし) |
| IV 秘密情報をクライアントへ出さない | `render.yaml`に`SECRET_KEY`等の実値を書かない。`sync: false`のみを記述する(FR-002) | PASS |
| V 契約駆動の境界 | 新規の依存追加なし。`package-lock.json`/`requirements.txt`とも変更なし | PASS |
| VI devcontainer固定 | Dockerイメージのビルド・起動確認は`dev`コンテナ内の`docker build`/`docker run`で行う(quickstart.md) | PASS |
| VII スケールを壊さない | `web`の`prod`起動は`$PORT`を読む(固定ポート待受にしない、FR-004) | PASS |

違反・トレードオフの正当化が必要な項目なし。Complexity Trackingは記入不要。

### Post-Design 再評価(Phase 1完了後)

Phase 1の設計成果物(research.md/data-model.md/quickstart.md)を反映しても、上表の判定に
変更はない。新規の永続化エンティティ・APIエンドポイント(`/api/`配下)は追加していない。
全項目PASS。

## Project Structure

### Documentation (this feature)

```text
specs/008-render-deploy-prep/
├── plan.md              # このファイル
├── research.md          # Phase 0 出力
├── data-model.md         # Phase 1 出力(該当なしを明記)
├── quickstart.md         # Phase 1 出力
└── tasks.md              # Phase 2 出力(/speckit-tasks が生成)
```

本featureは新規のAPI契約(`/api/`配下のエンドポイント)を追加しないため`contracts/`は
作成しない(`/healthz`は最小の200応答のみで、quickstart.mdに直接記載する)。

### Source Code (repository root)

```text
render.yaml                          # 新規: web / api / db の3サービス定義(docs/design.md §11)

apps/web/
├── Dockerfile                       # 新規: base → dev / prod マルチステージ(apps/api/Dockerfileと同方針)
├── .dockerignore                    # 新規: node_modules / .next / .git / .env を除外
├── next.config.js                   # 変更: output: "standalone" を追加(既存rewrites()はそのまま)
└── src/app/healthz/
    └── route.ts                     # 新規: GET → 200

apps/api/                            # 変更なし(既存のDockerfileをそのまま使用)
```

**Structure Decision**: `render.yaml`をリポジトリルートに追加し、`apps/web`に
コンテナ化とヘルスチェックのための最小限のファイルを追加する。`apps/api`と既存の
`apps/web`の画面コード(`src/app/board`等)には触れない。
