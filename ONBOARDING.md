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

## それ以外で困ったら

README.md → apps/api/README.md → docs/design.md → CONTRIBUTING.md → 聞く。
