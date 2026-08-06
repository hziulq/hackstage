# Feature Specification: Renderへのデプロイ準備(render.yaml / web Dockerfile / healthz)

**Feature Branch**: `008-render-deploy-prep`

**Created**: 2026-08-05

**Status**: Draft

**Input**: User description: "Renderへのデプロイ準備を整える。憲章・docs/design.md §11で仕様が決まっているRender Blueprint(render.yaml)を作成し、web(Next.js)側に不足しているDockerfile(dev/prodマルチステージ、apps/api/Dockerfileと同じ構成方針)とヘルスチェック用の/healthzルートを追加する。apiは既にprodターゲット付きDockerfileがあるためそのまま使う。dbはRenderマネージドPostgres 17をfromDatabaseでapiのDATABASE_URLに注入する構成にする。previewsはgeneration automaticでPRごとにweb+api+dbを複製する。render.yamlに秘密値を書かない(SECRET_KEYはsync: falseでダッシュボード入力)。buildFilter.pathsを設計値通りに設定し、pushごとの全再ビルドを避ける。実際にRenderダッシュボードでサービスを作成・接続する作業はユーザー自身が行うため、このfeatureのスコープはリポジトリ内のコード・設定ファイルの用意までとする。"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - リポジトリ管理者としてRender Blueprintでワンクリックにサービス一式を作成できる (Priority: P1)

リポジトリ管理者(自分)が、Renderダッシュボードでリポジトリを接続したとき、`render.yaml`を検出して
web・api・dbの3サービスをBlueprintとして一括作成できる。

**Why this priority**: `docs/design.md` §11で値まで決まっているにもかかわらず`render.yaml`自体が
存在しないため、現状Renderにデプロイする手段が無い。これが無いと他のどのユーザーストーリーも成立しない。

**Independent Test**: `render.yaml`をRenderの構文チェック(ダッシュボードのBlueprintプレビュー、または
`render-cli`相当の検証)に通し、web(docker/prod)・api(pserv/docker/prod)・db(Postgres 17)の3サービスが
`docs/design.md` §11の値通りに定義されていることを確認すれば、単独で価値を検証できる。

**Acceptance Scenarios**:

1. **Given** `render.yaml`がリポジトリルートに存在する、**When** Renderでこのリポジトリを新規Blueprintとして接続する、**Then** web・api・dbの3サービスが`docs/design.md` §11の設定値(rootDir・dockerTarget・healthCheckPath等)通りに提示される。
2. **Given** `render.yaml`に秘密値を書いていない、**When** `render.yaml`の内容を確認する、**Then** `SECRET_KEY`は`sync: false`として定義されており、値そのものはファイルに含まれない。

---

### User Story 2 - 開発者としてweb(Next.js)をコンテナ化された状態でRenderにデプロイできる (Priority: P1)

開発者が、`apps/web`をローカルの`compose.yaml`(dev)とRender(prod)の両方で同じ`Dockerfile`から
起動できる。

**Why this priority**: `apps/api`は既にdev/prodマルチステージの`Dockerfile`を持つが、`apps/web`には
存在しない。P1のBlueprint一括作成が機能しても、web側のイメージが無ければRenderでのビルドが失敗する。

**Independent Test**: `docker build --target prod`で`apps/web`のイメージをビルドし、コンテナ起動後に
`$PORT`で指定したポートでNext.jsアプリが応答することを確認すれば、単独で価値を検証できる。

**Acceptance Scenarios**:

1. **Given** `apps/web/Dockerfile`が追加されている、**When** `dev`ターゲットでビルド・起動する、**Then** ローカルの`compose.yaml`から起動した場合と同様に`npm run dev`相当の挙動になる。
2. **Given** `apps/web/Dockerfile`が追加されている、**When** `prod`ターゲットでビルド・起動する、**Then** Renderが注入する`$PORT`でNext.jsの本番ビルドが起動する。

---

### User Story 3 - Renderとしてwebサービスの死活監視ができる (Priority: P2)

Render(のヘルスチェック機構)が、`apps/web`にデプロイされたコンテナへ`/healthz`にアクセスし、
正常応答を得られる。

**Why this priority**: `docs/design.md` §11で`healthCheckPath: /healthz`が既に決まっているが未実装。
P1が完了していてもヘルスチェックが無いとRenderがデプロイ後にサービスを正常と判定できず、
ゼロダウンタイムデプロイやオートリスタートが機能しない。P1(そもそも動く)よりは影響範囲が狭いためP2。

**Independent Test**: デプロイ後(またはローカルで`prod`起動後)に`/healthz`へGETし、200系の応答が
返ることを確認すれば、単独で価値を検証できる。

**Acceptance Scenarios**:

1. **Given** `apps/web`が起動している、**When** `/healthz`にGETする、**Then** 200が返る。
2. **Given** `apps/web`が起動している、**When** `/api/*`以外の未知のパスにアクセスする、**Then** `/healthz`の追加によって既存のルーティングが壊れていない。

---

### Edge Cases

- `render.yaml`の`previews: generation: automatic`によりPRごとにweb+api+dbが複製されるが、Preview用のDB(空のPostgres)にはマイグレーションが自動適用されない(`007-ci-setup`のCIで判明した「フレッシュDBにテーブルが無い」問題と同種)。本featureはこの問題の解消を範囲に含めるか?
- `apps/web`に`output: standalone`等のビルド設定が無い場合、Dockerイメージが不必要に大きくなる可能性がある。
- `buildFilter.paths`の設定を誤ると、`apps/web`のみの変更で`api`まで再ビルドされる(または逆)無駄が発生する。

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: システムは、リポジトリルートに`render.yaml`を持ち、`docs/design.md` §11で定義された値(`web`/`api`/`db`のサービス定義、`buildFilter.paths`、`previews.generation: automatic`)を反映しなければならない。
- **FR-002**: `render.yaml`は、`SECRET_KEY`等の秘密値をファイルに直接書いてはならず、`sync: false`としてダッシュボード入力に委ねなければならない(憲章 原則IV)。
- **FR-003**: `render.yaml`は、`dev`サービスを含めてはならない(`docs/design.md` §11)。
- **FR-004**: システムは、`apps/web`に`dev`/`prod`のマルチステージ`Dockerfile`を持たなければならない。`prod`ターゲットは`$PORT`環境変数で指定されたポートで本番ビルドを起動しなければならない。
- **FR-005**: `apps/web`の`Dockerfile`は、`apps/api/Dockerfile`と同じ構成方針(ローカル/Render共通のDockerfile、ステージ名`dev`/`prod`)に従わなければならない。
- **FR-006**: システムは、`apps/web`に`/healthz`エンドポイントを持ち、正常時に200を返さなければならない。
- **FR-007**: `render.yaml`の`db`定義は、Render管理のPostgres(バージョン17。`compose.yaml`の`postgres:17`と一致)を`fromDatabase`で`api`サービスの`DATABASE_URL`に注入しなければならない。
- **FR-008**: 本featureは、リポジトリ内のコード・設定ファイルの用意までを範囲とし、Renderダッシュボード上でのサービス作成・接続・秘密値の入力は対象外とする(ユーザー自身が行う)。

### Key Entities

該当なし。

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `render.yaml`をRenderのBlueprint検証にかけると、追加の手動修正なしにweb・api・dbの3サービスが作成候補として提示される。
- **SC-002**: `apps/web`を`prod`ターゲットでビルド・起動すると、`$PORT`で指定した任意のポートで応答する。
- **SC-003**: 起動済みの`apps/web`に対して`/healthz`にアクセスすると200が返る。
- **SC-004**: `render.yaml`のいずれの値にも秘密情報(パスワード・APIキー等の実値)が含まれていない。

## Assumptions

- Preview環境(`007-ci-setup`同様のフレッシュDB問題)へのマイグレーション自動適用は本featureの範囲外とする。既知の課題として`Edge Cases`に記録し、解消は別featureに委ねる。
- `apps/web`のNext.jsビルド設定(`output: standalone`等)の追加は、`prod`ターゲットのDockerfileを妥当なサイズ・起動速度にするための実装判断として本feature内で行うが、詳細な最適化(マルチアーキテクチャ対応等)は範囲外とする。
- Renderの実際のプラン選定(Freeプラン/Starterプラン等)は`docs/design.md` §11の「未定」のままとし、本featureでは変更しない。
- `render.yaml`の`web`サービスの`buildFilter.paths`に`openapi.json`を含める(design.md記載通り。web側の型生成が将来openapi.jsonを参照する前提のため)。

## 既知の課題(本feature範囲外)

- **`apps/web`の`next build`が既存コード側の原因で失敗する。** 本feature追加分(`output: "standalone"`, `Dockerfile`, `/healthz`)を`git stash`で取り除いた状態でも同一のビルド失敗が再現することを確認済み。`src/app/page.tsx`の内容(`redirect`の有無)にも依存せず、Next.js自身の内部エラーページ(`/_global-error`)のプリレンダリングでも同種のエラー(`Cannot read properties of null (reading 'useContext')`)が発生するため、原因は個別ページではなく`layout.tsx`/`BottomNav.tsx`かNext.js 16.3.0/React 19.2.8の組み合わせにあると推測される。
- この既存バグの修正は本feature(`008-render-deploy-prep`)の範囲外とする(spec.mdで合意した「既存コードへの変更はゼロ」の方針を優先する)。`render.yaml`・`apps/web/Dockerfile`・`/healthz`の実装自体は設計通りに完了しているが、このバグが解消されるまで実際に`docker build --target prod`・Renderへの実デプロイは成功しない。
- 別feature(担当者はweb側の骨格を作った担当者を想定)でこの`next build`失敗を解消することを推奨する。
