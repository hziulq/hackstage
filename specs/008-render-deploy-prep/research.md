# Phase 0 Research: Renderへのデプロイ準備(render.yaml / web Dockerfile / healthz)

## 1. render.yamlの構成

- **Decision**: リポジトリルートに`render.yaml`を新規作成する。`web`(`type: web`, `runtime: docker`)・`api`(`type: pserv`, `runtime: docker`)・`db`(`databases:`)の3サービスを、`docs/design.md` §11の値をそのまま反映する。
- **Rationale**: 値は既に`docs/design.md` §11で確定済み。憲章 原則I(規約は1箇所にのみ書く)により、`render.yaml`は設計値を再定義せず、そのまま実装するだけでよい。
- **Alternatives considered**: なし(設計値が既に一意に決まっているため検討不要)。

## 2. web用Dockerfileの構成(dev/prodマルチステージ)

- **Decision**: `apps/api/Dockerfile`と同じ構成方針(単一Dockerfile、`base`ステージから`dev`/`prod`を分岐)を採用する。`prod`ステージは`next build`(`output: "standalone"`)の生成物(`.next/standalone`, `.next/static`, `public`)のみをコピーし、`node server.js`で起動する。`dev`ステージはソースをvolumeマウントする前提で`npm run dev`を実行する。
- **Rationale**: `docs/design.md` §4で「web prod: `next start`(standalone)/`$PORT`」と明記されている。`output: "standalone"`はNext.jsが`node_modules`を含む自己完結サーバーを`.next/standalone`に生成する機能で、Dockerイメージを`node_modules`全体を含めるより軽量にできる(Next.js公式のDocker推奨パターン)。`apps/api`の`Dockerfile`が`base`→`dev`/`prod`の1ファイル構成なので、`web`も同じ方針に揃える(構成方針の不一致を避ける)。
- **Alternatives considered**: `next start`をそのまま`prod`ステージで実行する案 — `node_modules`全体(devDependencies含む)をイメージに含める必要があり、`standalone`より重い。今回は採用しない。

## 3. `$PORT`の扱い(web)

- **Decision**: `standalone`出力の`server.js`は`process.env.PORT`(未設定時は3000)を自動的に読む。追加のラッパースクリプトは書かず、`CMD ["node", "server.js"]`とし、`ENV PORT=3000`をdevのデフォルトとして設定する(Renderは`PORT`を自動注入するため`prod`側で上書きされる)。
- **Rationale**: `docs/design.md` §9で「`PORT`(web) | 本番: Renderが自動注入(値に依存しない)」とある。`next build --standalone`で生成される`server.js`はNext.js側で`process.env.PORT`を読む実装になっており、追加のシェルラッパー(`apps/api`の`sh -c "gunicorn ... ${PORT}"`のような明示展開)は不要。

## 4. `/healthz`ルートの実装

- **Decision**: `apps/web/src/app/healthz/route.ts`にRoute Handlerを追加し、`GET`で`200`(`{"status":"ok"}`程度の最小応答)を返す。
- **Rationale**: `docs/design.md` §6で「`web`自身が返すのは`/healthz`のみ(`/api/`の外)」と明記されており、`app/api/**/route.ts`を作らない制約(憲章 原則II)に抵触しない場所として`/healthz`が唯一許可されている。DBやapiへの到達性チェックは行わず、プロセスが応答可能かどうかのみを返す(Renderのヘルスチェックはコンテナの起動確認が目的であり、依存先の健全性まで含めると誤検知でデプロイが失敗しやすくなるため)。
- **Alternatives considered**: `/api/health`(既にapiに実装済み)への相乗り — 原則II(`web`から`api`を絶対URLで呼ぶのはServer Component/Server Actionの規約であり、ヘルスチェックは軽量・依存なしであるべき)から見送り、`web`単体で200を返す実装とする。

## 5. `next.config.js`の変更範囲

- **Decision**: 既存の`rewrites()`はそのまま残し、`output: "standalone"`のみを追加する。
- **Rationale**: `rewrites()`は`API_INTERNAL_URL`が無い間は空配列を返す既存の分岐がある(ローカルの一時的な状態を壊さない設計)。今回の変更はビルド出力形式の追加のみであり、既存のロジックに影響しない。

## 6. buildFilter.pathsの設定

- **Decision**: `web`の`buildFilter.paths`は`apps/web/**`と`openapi.json`(`docs/design.md` §11記載通り)。`api`の`buildFilter.paths`は`apps/api/**`。
- **Rationale**: 設計値通り。`openapi.json`をwebのbuildFilterに含めるのは、将来web側が`openapi.json`からTypeScript型を生成する際にopenapi.jsonの変更でwebの再ビルドが必要になるため(憲章 原則V)。

## 7. previewのDBマイグレーション未適用問題

- **Decision**: 本feature(`008-render-deploy-prep`)の範囲外とする。既知の課題としてspec.mdの`Edge Cases`/`Assumptions`に記録済み。
- **Rationale**: `007-ci-setup`のCIで判明した「フレッシュDBにテーブルが無い」問題と同種の課題であり、Render Previewの`db`(`fromDatabase`で作られる新規Postgres)にも同じ課題が生じる。しかし本featureのスコープは「リポジトリ内のコード・設定ファイルの用意まで」(spec.md FR-008)であり、マイグレーション自動実行の仕組み(Renderの`preDeployCommand`等)を導入するかどうかは別途判断が必要な設計決定であるため、本featureには含めない。

## 8. `.dockerignore`(web)

- **Decision**: `apps/web/.dockerignore`を新規作成する。`node_modules`, `.next`, `.git`, `.env`を除外する。
- **Rationale**: `docs/design.md` §3のディレクトリ構成で`apps/web/.dockerignore`が既に定義済み(未作成のまま)。`apps/api/.dockerignore`と同じ方針(ビルド不要物の除外)に揃える。

## 未解決のNEEDS CLARIFICATION

なし。
