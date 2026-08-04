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
(`app/config.py` の `Config.DATABASE_URL` から読める)。db サービス自体は起動済みなので、
繋ぐ処理を書けばそのまま使える。

このリポジトリはまだ ORM を選定・インストールしていない。`requirements.txt` に
必要なライブラリを追加してから使う。

```bash
# 例: SQLAlchemy を使う場合(ホスト側のターミナルで)
echo "SQLAlchemy==2.0.35" >> requirements.txt
echo "psycopg2-binary==2.9.9" >> requirements.txt
docker compose build api
docker compose up -d api
```

```python
# 接続確認の例(app/config.py の DATABASE_URL を使う)
from sqlalchemy import create_engine, text

engine = create_engine(Config.DATABASE_URL)
with engine.connect() as conn:
    conn.execute(text("select 1"))
```

## マイグレーション・認証について

Alembic(マイグレーション)・Flask-Login(認証)はまだ入れていない。必要になった時点で
`requirements.txt` に追加し、`docs/design.md` §7・§8 の契約(エンドポイント・Cookie属性)に
沿って実装する。
