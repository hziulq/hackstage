---

description: "Task list template for feature implementation"
---

# Tasks: Renderへのデプロイ準備(render.yaml / web Dockerfile / healthz)

**Input**: Design documents from `/specs/008-render-deploy-prep/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md(すべて生成済み)

**Tests**: 本feature自体は構成ファイル・最小エンドポイントの追加であり、`quickstart.md`の
ローカル再現手順(`docker build`/`docker run`/`curl`)で検証する。新規のpytest/jestテストは追加しない。

**Organization**: spec.mdのUser Story(P1×2、P2×1)ごとにグルーピングする。

## Format: `[ID] [P?] [Story] Description`

- **[P]**: 並行実行可能(別ファイル・依存なし)
- **[Story]**: US1=Render Blueprint(render.yaml)一括作成, US2=webのコンテナ化, US3=webのヘルスチェック

---

## Phase 1: Setup

**Purpose**: web側のビルド設定(standalone出力)を先に用意する。US2・US3の前提。

- [X] T001 `apps/web/next.config.js`に`output: "standalone"`を追加する(既存の`rewrites()`はそのまま残す)
- [X] T002 [P] `apps/web/.dockerignore`を新規作成し、`node_modules`, `.next`, `.git`, `.env`を除外する

---

## Phase 2: User Story 2 - 開発者としてweb(Next.js)をコンテナ化された状態でRenderにデプロイできる (Priority: P1) 🎯 MVP

**Goal**: `apps/web`が`apps/api`と同じ方針のdev/prodマルチステージ`Dockerfile`を持ち、`prod`ターゲットが`$PORT`で起動する

**Independent Test**: `docker build --target prod`でビルドし、`-e PORT=<任意の値>`で起動して指定したポートで応答することを確認する

### Implementation for User Story 2

- [X] T003 [US2] `apps/web/Dockerfile`を新規作成する。`base`ステージ(Node 22、`package*.json`をコピーして`npm ci`)→ `dev`ステージ(`CMD ["npm", "run", "dev"]`)/ `builder`ステージ(`npm run build`)→ `prod`ステージ(`builder`から`.next/standalone`・`.next/static`・`public`のみをコピーし`CMD ["node", "server.js"]`)の構成にする(T001, T002に依存)
- [ ] T004 [US2] **ブロック**: `quickstart.md`の「webのDockerイメージ(prod)のビルド・起動確認」は、既存コード側の`next build`失敗(spec.mdの「既知の課題」参照)により実行できない。この環境にDockerが無いため`docker build`自体も実行できていない(T003に依存)
- [X] T005 [US2] `apps/web`の`dev`ステージと同じコマンド(`npm run dev`)をローカルで直接実行し、`http://localhost:3000/`が`/timeline`への307リダイレクトで応答することを確認した(`docker build --target dev`はこの環境にDockerが無く実行できないため、Dockerfileが実行するコマンドと同じ手順で代替検証。T003に依存)

**Checkpoint**: `apps/web`がローカルで`docker build --target prod`/`dev`の両方から起動できる

---

## Phase 3: User Story 3 - Renderとしてwebサービスの死活監視ができる (Priority: P2)

**Goal**: `/healthz`が200を返し、Renderのヘルスチェックに使える

**Independent Test**: 起動済みの`apps/web`に`curl`で`/healthz`を叩き200が返ることを確認する

### Implementation for User Story 3

- [X] T006 [US3] `apps/web/src/app/healthz/route.ts`を新規作成し、`GET`で`200`(最小のJSON応答)を返すRoute Handlerを実装する(T003に依存。同じイメージで確認するため)
- [X] T007 [US3] `npm run dev`で起動したサーバーに対して`curl -i http://localhost:3000/healthz`を実行し、`200`と`{"status":"ok"}`が返ることを確認した(prodコンテナでの確認はT004がブロック中のため、devサーバーで代替検証。ルートハンドラ自体の動作はdev/prodで差が無いため妥当。T006に依存)

**Checkpoint**: `/healthz`がprodビルドで200を返す

---

## Phase 4: User Story 1 - リポジトリ管理者としてRender Blueprintでワンクリックにサービス一式を作成できる (Priority: P1)

**Goal**: `render.yaml`がリポジトリルートに存在し、`docs/design.md` §11の値通りに`web`/`api`/`db`を定義する

**Independent Test**: `render.yaml`をYAMLとして読み込めることを確認し、3サービスの値を目視で`docs/design.md` §11と照合する

### Implementation for User Story 1

- [X] T008 [US1] リポジトリルートに`render.yaml`を新規作成し、`web`サービス(`type: web`, `runtime: docker`, `rootDir: apps/web`, `dockerfilePath: ./Dockerfile`, `dockerContext: .`, `dockerTarget: prod`, `healthCheckPath: /healthz`, `buildFilter.paths: [apps/web/**, openapi.json]`)を定義する(T003, T006に依存。参照するDockerfile/healthzが存在してから記述する)
- [X] T009 [US1] `render.yaml`に`api`サービス(`type: pserv`, `runtime: docker`, `rootDir: apps/api`, `dockerfilePath: ./Dockerfile`, `dockerContext: .`, `dockerTarget: prod`, `envVars`に`PORT: 8000`(明示)と`SECRET_KEY`(`sync: false`), `buildFilter.paths: [apps/api/**]`)を追加する(T008に依存。同一ファイルへの追記のため順次実施)
- [X] T010 [US1] `render.yaml`に`databases:`で`db`(`name: db`, `postgresMajorVersion: 17`)を追加し、`api`サービスの`envVars`に`DATABASE_URL`を`fromDatabase`(`name: db`, `property: connectionString`)で注入する設定を追加する(T009に依存)
- [X] T011 [US1] `render.yaml`のトップレベルに`previews: {generation: automatic}`を追加する。`dev`サービスが含まれていないこと、秘密値の実値が書かれていないことを目視確認する(T010に依存)
- [X] T012 [US1] `quickstart.md`の「render.yamlの構文・値の確認」を実行し、`yaml.safe_load`が例外なく成功することと、`docs/design.md` §11の値との一致を確認する(T011に依存)

**Checkpoint**: `render.yaml`が3サービス分完成し、構文チェックを通過する

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: 憲章・設計文書との整合の最終確認

- [X] T013 憲章のセキュリティチェックリスト(`.specify/memory/constitution.md`)のうち本featureに関係する項目(「秘密値がリポジトリ・render.yamlに入っていない」「クライアントコードにapiの絶対URLが無い」)を`render.yaml`・`apps/web`の変更に対して照合する
- [X] T014 `docs/design.md` §3のディレクトリ構成表(`apps/web/Dockerfile`, `apps/web/.dockerignore`, `render.yaml`)と実際の追加ファイルが一致していることを確認する(食い違いがあればdocs/design.mdを先に更新するか実装を合わせる。憲章 原則I)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: 依存なし。即着手可
- **User Story 2 (Phase 2)**: Setup完了後
- **User Story 3 (Phase 3)**: User Story 2完了後(同じDockerイメージで確認するため)
- **User Story 1 (Phase 4)**: User Story 2・3完了後(render.yamlがdockerfilePath/healthCheckPathを参照するため)
- **Polish (Phase 5)**: 全User Story完了後

### User Story Dependencies

- **US2(webのコンテナ化, P1)**: Setup完了後に開始可。他Storyに依存しない
- **US3(healthz, P2)**: US2のDockerfileが無いと`prod`ビルドでの確認ができないため、US2完了後
- **US1(render.yaml, P1)**: US2・US3が参照先(Dockerfile・healthCheckPath)を提供するため、実装順としては最後だが優先度はP1(spec.mdのUser Story優先度と実装順は一致しない。render.yaml自体の価値はP1だが、参照先が無いと検証できないため実装順を後ろにした)

### Parallel Opportunities

- Setup: T001とT002は別ファイルのため並行可能
- Phase 2〜4は同一ディレクトリ・同一ファイルへの追記が多く、直列実行が安全

---

## Implementation Strategy

### MVP First (User Story 2)

1. Phase 1: Setup(standalone出力の有効化)
2. Phase 2: US2(webのコンテナ化)— ここまでで「webがRenderにデプロイ可能な形になる」という最小価値が完成
3. **STOP and VALIDATE**: `docker build --target prod`と起動確認

### Incremental Delivery

1. Setup → standalone出力の有効化
2. US2(webのコンテナ化)→ 独立検証(MVP到達)
3. US3(healthz)→ 独立検証
4. US1(render.yaml)→ 独立検証(3サービスの構成完成)
5. Polish(憲章・設計文書との整合確認)

---

## Notes

- 各タスク完了後にコミットすることを推奨する。
- Renderダッシュボード上での実際のサービス作成・接続・`SECRET_KEY`入力はこのタスクリストの範囲外(ユーザー自身が行う)。
- **T004は既存コード側の`next build`失敗によりブロック中**(spec.mdの「既知の課題」参照)。この環境にDockerが無いため`docker build`自体も未実施。`Dockerfile`/`render.yaml`/`/healthz`の実装は完了しており、既存バグ解消後にT004・T007のprodコンテナでの検証を別途実施することを推奨する。
