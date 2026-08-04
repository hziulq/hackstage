# Flask(api) 最初に読むメモ

手順の正本は `README.md` / `apps/api/README.md`。ここには**そこに書いてない詰まりポイントだけ**を書く。

## これだけ覚える

- **`localhost:8000` はブラウザからもホストのターミナルからも繋がらない。故障ではなく仕様。**
  `api` は非公開設計（憲章 原則II）。確認は必ず **`dev` コンテナの中**から:
  ```bash
  curl http://api:8000/api/health
  ```
  （`localhost` ではなくサービス名 `api` を使う）

- `requirements.txt` を変えても保存しただけでは反映されない。ターミナルは不要、GUIで完結する:
  1. 画面左下の緑色のアイコン（`Dev Container: hackstage`）をクリック
  2. **「Rebuild Container」** を選ぶ
     （コマンドパレット `F1` → `Dev Containers: Rebuild Container` でも同じ）
  - これで `api` も含めて必要なコンテナが作り直される。少し時間がかかるが待つだけでよい。
  - DBのデータは消えない（`db-data` volumeに永続化されているため、コンテナを作り直しても残る）。

## DB

- 疎通確認・SQLAlchemyでの接続例は `README.md`（`psql "$DATABASE_URL"`）と
  `apps/api/README.md`「DBに接続する」節にすでにある。まずそこを見る。
- `DATABASE_URL` は `compose.yaml` が自動生成して渡す。`.env` に書かない。
- ハマったら疑うのは大体これ: `.env` の `POSTGRES_PASSWORD` が空 → `db` が起動失敗 →
  `api` も `dev` も巻き添えで止まる。

## マイグレーション(Alembic)って何?

**「DBのテーブル構造を作る・変える作業に、いつ誰がやったかの履歴をつける仕組み」**だと思ってください。
テーブルの定義自体は `apps/api/app/models/` に書かれている(SQLAlchemyのクラス)。
そこから実際にDBへ`CREATE TABLE`する手順書を作って実行するのがAlembic。

手順の正本は `apps/api/README.md`「マイグレーション」節。ここでは初めて触る人向けに、
**最初の1回だけ**やることを順番に書く。

### 初めて `flask db upgrade` を実行するまでの手順

1. `.env` がある状態で、devcontainerを開く(`dev` / `db` / `api` が起動する)
2. `git pull` して、このマイグレーションが入ったブランチ・コミットを取り込む
3. `dev` コンテナのターミナルで一度だけ:
   ```bash
   pip install --user -r apps/api/requirements.txt
   ```
   (`post-create.sh` で自動化されているので、コンテナを**作り直した場合は不要**。
   既存のコンテナに後から`git pull`した場合は手動で1回実行する)
4. 同じターミナルで:
   ```bash
   cd apps/api
   export FLASK_APP=wsgi.py
   flask db upgrade
   ```
5. 最後に何もエラーが出ず、`INFO  [alembic.runtime.migration] Running upgrade  -> ...` の
   ような行が出れば成功。`psql "$DATABASE_URL" -c "\dt"` でテーブルが12個くらい
   増えていれば完了。

### 詰まりやすい点

- **`flask: command not found` になる** → 手順3を忘れている(パッケージが入っていない)。
- **「`type "..." already exists`」のようなエラーが出る** → 過去に自分で`db.create_all()`や
  手動の`CREATE TABLE`でテーブル・ENUM型を作ったことがあるDBに対して実行している。
  ローカルDBのデータは消えて困るものではないはずなので、一番簡単なのは
  **DBをまるごと作り直す**こと:
  ```bash
  # ホスト側のターミナルで(dev コンテナには docker CLI が無いため)
  docker compose down
  docker volume rm hackstage_db-data
  docker compose up -d db
  ```
  その後もう一度 手順4 をやり直す。
- **`flask db init` を自分でもう一度実行してしまった** → `migrations/`は1回作ったら
  リポジトリで共有するものなので、**自分で作り直す必要はない**。誤って実行した場合は
  `git checkout -- migrations/` で戻す。
- **今の自分のDBが何のリビジョンまで進んでいるか分からない** →
  `flask db current`(今の状態)と`flask db history`(全履歴)で確認できる。

### これだけは覚えておく

- モデル(`app/models/`)を書き換えたら、**自動でDBが変わるわけではない**。
  `flask db migrate -m "説明"` → 生成された`migrations/versions/*.py`の内容を確認 →
  `flask db upgrade` の3手順を必ず踏む。
- 生成された`migrations/versions/*.py`はコミットする対象。生成しただけでpushし忘れると、
  他の人は新しいテーブルを知らないまま作業してしまう。

## それ以外で困ったら

README.md → apps/api/README.md → docs/design.md → CONTRIBUTING.md → 聞く。
