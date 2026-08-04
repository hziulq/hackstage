# apps/api

Flask バックエンド。規約・環境変数・API契約は `docs/design.md` を参照(ここには再掲しない)。

## 起動

`devcontainer.json` の `runServices` に含まれているため、VS Code で
**Reopen in Container** するだけで `dev`・`db` と一緒に自動で起動する。手動での
`docker compose up` は不要。

動作確認は `dev` コンテナ内(VS Code の統合ターミナル)から:

```bash
curl -s http://api:8000/api/health
# => {"status": "ok"}
```

`api` は `expose` のみでホストに公開していない(憲章 原則II)。ホストの `curl`/ブラウザからは
直接届かない。確認は `dev` コンテナ経由で行う。

`requirements.txt` を変更した(パッケージを追加した)場合だけ、ホスト側のターミナルで
再ビルドが必要(`dev` コンテナには Docker CLI が無いため):

```bash
docker compose build api
docker compose up -d api
```

コードは `apps/api:/app` を volume マウントしているので、`app/` 以下を編集すれば
`flask run --debug` のホットリロードで即反映される。

## 構成

```
app/
├── __init__.py   # create_app()。Blueprint はここで登録する
├── config.py     # 環境変数の読み込み
└── routes/       # エンドポイントを追加する場所
```

新しいエンドポイントは `app/routes/` に Blueprint を追加し、`app/__init__.py` の
`create_app()` で `register_blueprint` する。

## DB に接続する

`DATABASE_URL` は `compose.yaml` が組み立てて、このコンテナに既に渡っている
(`app/config.py` の `Config.DATABASE_URL` / `SQLALCHEMY_DATABASE_URI` から読める)。
db サービス自体は起動済みなので、繋ぐ処理を書けばそのまま使える。

ORM は Flask-SQLAlchemy を採用済み。モデルは `app/models/` にある
(`app/models/__init__.py` で全モデルをインポートし、Alembic の autogenerate が
検出できるようにしている)。

## マイグレーション（Alembic / Flask-Migrate）

マイグレーション本体はリポジトリルート直下の `migrations/`（このディレクトリではない）にある。
理由と実行場所は `docs/design.md` §3、並行マイグレーションの運用は `CONTRIBUTING.md` §5 を参照。

**`dev` コンテナから実行する。`api` コンテナには `apps/api` しかマウントされておらず、
`migrations/` が見えないため。**

```bash
# dev コンテナ内、apps/api で
cd apps/api
export FLASK_APP=wsgi.py

# 全員が同じスキーマを再現する（新しく clone した場合・pull で新しいリビジョンが来た場合）
flask db upgrade

# モデルを変更した後、新しいリビジョンを生成する
flask db migrate -m "変更内容"
flask db upgrade

# 適用状況の確認
flask db current
flask db history
```

- `flask db init` は実行済み（`migrations/` が存在する）。**再実行しないこと**（既存履歴を壊す）。
- `dev` コンテナには `.devcontainer/post-create.sh` が `apps/api/requirements.txt` を
  インストールするため、`flask` コマンドはコンテナ作成時から使える。
  `requirements.txt` を変更した場合は `pip install --user -r apps/api/requirements.txt` を
  `dev` コンテナ内で再実行する（`api` コンテナ用の再ビルドとは別。上の「起動」節を参照）。
- Autogenerate は ENUM 型の列の変更を完全には検出できないことがある。生成後は必ず差分を目で確認する。

## 認証について

Flask-Login はまだ入れていない。必要になった時点で `requirements.txt` に追加し、
`docs/design.md` §8 の契約(エンドポイント・Cookie属性)に沿って実装する。
