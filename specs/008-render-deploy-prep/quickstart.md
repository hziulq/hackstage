# Quickstart: Renderデプロイ準備の動作確認

Renderへの実際の接続は行わず、`dev`コンテナ内でローカルに再現できる範囲を確認する。

> **既知の制約**: 現時点で`apps/web`の`npm run build`(`next build`)が既存コード側の原因で
> 失敗する(spec.mdの「既知の課題」参照)。このため以下の`docker build --target prod`の
> 手順は、既存バグが解消されるまで成功しない。`Dockerfile`・`render.yaml`・`/healthz`の実装自体は
> 設計通りであり、バグ解消後はこの手順がそのまま通る想定。

## webのDockerイメージ(prod)のビルド・起動確認

```bash
cd apps/web
docker build --target prod -t hackstage-web-prod .
docker run --rm -e PORT=4000 -p 4000:4000 hackstage-web-prod
```

**期待結果**: コンテナが起動し、`http://localhost:4000/`にアクセスするとトップページが表示される。
`$PORT`を別の値(例: 5000)に変えて再実行しても、指定したポートで応答する(`docs/design.md` §9)。

## webのDockerイメージ(dev)の起動確認

```bash
cd apps/web
docker build --target dev -t hackstage-web-dev .
docker run --rm -p 3000:3000 -v "$(pwd):/app" hackstage-web-dev
```

**期待結果**: `compose.yaml`経由の`web`サービスと同様に、ホットリロード付きの開発サーバーが
`http://localhost:3000/`で応答する。

## `/healthz`の確認

```bash
curl -i http://localhost:4000/healthz
```

**期待結果**: `200`が返る。認証不要・依存先(api/db)への到達性チェックは行わない
(`docs/design.md` §6: `web`自身が返すのは`/healthz`のみ)。

## render.yamlの構文・値の確認

```bash
# YAMLとして構文が正しいことのみをローカルで確認する(Render固有のスキーマ検証は
# ダッシュボードでのBlueprint作成時にのみ行われる)
python3 -c "import yaml; yaml.safe_load(open('render.yaml'))"
```

**期待結果**: 例外なく読み込める。`web`/`api`/`db`の3サービスが定義され、`dev`サービスが
含まれていないこと、`SECRET_KEY`に実値が書かれていないこと(`sync: false`のみ)を目視で確認する。

## Renderへの実接続確認(このfeatureの範囲外・参考)

以下はユーザー自身がRenderダッシュボードで行う(本featureのスコープ外):

1. Renderで「New +」→「Blueprint」からこのリポジトリを接続する
2. `render.yaml`が検出され、`web`/`api`/`db`の3サービスが提案されることを確認する
3. `api`サービスの`SECRET_KEY`を手入力する
4. デプロイ後、`web`サービスのURLにアクセスしてトップページが表示されることを確認する
