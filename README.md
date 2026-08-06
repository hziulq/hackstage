# hackstage

Next.js (web) + Flask (api) + PostgreSQL。Render にデプロイする。

## 規約はこの 3 文書にある

作業を始める前に読むこと。**規約値は本 README に再掲しない**（1 箇所にのみ書く方針のため）。

| 文書 | 内容 |
|---|---|
| [`.specify/memory/constitution.md`](.specify/memory/constitution.md) | **憲章**。原則・禁止事項・レビューゲート。全員が一度読む |
| [`docs/design.md`](docs/design.md) | 技術スタック・構成・環境変数・API 契約・Render 設定値。実装中に引く |
| [`CONTRIBUTING.md`](CONTRIBUTING.md) | ブランチ運用・PR 手順・マージ衝突の解消・Spec Kit の使い方 |

## 起動手順

開発はすべて devcontainer 内で行う。ホストに Node や Python を入れる必要はない。

### 1. `.env` を作る

```bash
cp .env.example .env
```

`POSTGRES_PASSWORD` と `SECRET_KEY` を埋める。どちらもローカル専用の任意の値でよい。

> この手順を飛ばすと `db` が起動に失敗する:
> `Database is uninitialized and superuser password is not specified.`

### 2. devcontainer で開く

VS Code でリポジトリを開き、コマンドパレットから **Dev Containers: Reopen in Container**。

`dev`・`db`・`api` が起動し、`dev` コンテナの中に入る。初回はイメージのビルドに数分かかる。

### 3. 動作確認

`dev` コンテナ内で:

```bash
node -v          # v22.x
python --version # 3.12.x
pwsh --version   # 7.x
psql --version   # 17.x

psql "$DATABASE_URL" -c 'select 1'   # db に到達できるか
```

## VS Code を使わない場合

```bash
docker compose up -d db          # DB だけ起動
docker compose run --rm dev bash # 作業用コンテナに入る
```

`.devcontainer/Dockerfile` にツールを明示しているので、VS Code 経由でも
`docker compose` 経由でも同じ中身になる。

## デプロイ

本番は `render.yaml`（Render Blueprint）を正とする。審査など最長3日程度の短期利用に限っては、
[`docs/vps-deploy.md`](docs/vps-deploy.md) のVPS(Vultr)手順を使う。

## 現状

`apps/api` の骨格が入り、`api` サービスは devcontainer を開くと自動で起動する
(詳細は `apps/api/README.md`)。

`apps/web` はまだ空。`compose.yaml` の `web` サービスは `profiles: [app]` を付けて
既定では起動しないようにしてある。フロントエンド担当が骨格（`package.json`）を置く PR で
有効化する。手順は `compose.yaml` のコメントにある。

それまでは `dev` コンテナ内で `npm run dev` を起動すれば、ホストの `localhost:3000` から見える。
