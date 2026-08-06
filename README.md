# Hackstage

Hackstage は、Next.js・Flask・PostgreSQL を使用したフルスタック Web アプリケーション向けのモノレポです。

開発環境は Dev Container を前提としており、Node.js、Python、PostgreSQL をローカル環境へインストールすることなく開発を開始できます。すべての開発環境は Docker Compose により構築され、Render へのデプロイを想定した構成になっています。

---

## 規約はこの3文書にある

作業を始める前に読むこと。**規約値は本READMEに再掲しない**（1箇所にのみ書く方針のため）。

| 文書 | 内容 |
|---|---|
| [`.specify/memory/constitution.md`](.specify/memory/constitution.md) | **憲章**。原則・禁止事項・レビューゲート。全員が一度読む |
| [`docs/design.md`](docs/design.md) | 技術スタック・構成・環境変数・API 契約・Render 設定値。実装中に引く |
| [`CONTRIBUTING.md`](CONTRIBUTING.md) | ブランチ運用・PR 手順・マージ衝突の解消・Spec Kit の使い方 |

---

## 概要

- Next.js と Flask を利用したフルスタック構成
- PostgreSQL を利用したデータベース環境
- Dev Container による統一された開発環境
- Docker Compose によるサービス管理
- OpenAPI による API 定義
- Render を前提としたデプロイ構成

---

## 動作環境

開発には以下が必要です。

| ソフトウェア | バージョン |
|--------------|-----------|
| Docker Desktop | 最新版 |
| Visual Studio Code | 最新版 |
| Dev Containers 拡張機能 | 最新版 |
| Git | 最新版 |

Node.js、Python、PostgreSQL をローカルへインストールする必要はありません。

---

## はじめに

### 1. リポジトリを取得

```bash
git clone <repository-url>
cd hackstage
```

### 2. 環境変数を作成

```bash
cp .env.example .env
```

以下の値を設定してください。

```
POSTGRES_PASSWORD=
SECRET_KEY=
```

ローカル開発では任意の値で問題ありません。

設定しない場合、PostgreSQL は次のようなエラーで起動できません。

```text
Database is uninitialized and superuser password is not specified.
```

### 3. Dev Container を起動

Visual Studio Code でリポジトリを開き、

```
Dev Containers: Reopen in Container
```

を実行してください。

初回のみイメージのビルドに数分かかります。

起動後、以下のサービスが自動的に開始されます。

| サービス | 内容 |
|----------|------|
| dev | 開発環境 |
| db | PostgreSQL |
| api | Flask API |

### 4. 動作確認

Dev Container 内で以下を実行してください。

```bash
node -v
python --version
pwsh --version
psql --version

psql "$DATABASE_URL" -c "select 1"
```

期待されるバージョンは以下のとおりです。

| ソフトウェア | バージョン |
|--------------|-----------|
| Node.js | 22.x |
| Python | 3.12.x |
| PowerShell | 7.x |
| PostgreSQL Client | 17.x |

最後のコマンドが正常終了すれば、データベースへの接続は完了しています。

---

## VS Code を利用しない場合

Docker Compose を利用して開発環境を起動できます。

```bash
docker compose up -d db

docker compose run --rm dev bash
```

どちらの方法でも `.devcontainer/Dockerfile` で定義された同一の開発環境が利用されます。

---

## デプロイ

本番は `render.yaml`（Render Blueprint）を正とする。審査など最長3日程度の短期利用に限っては、
[`docs/vps-deploy.md`](docs/vps-deploy.md) のVPS(Vultr)手順を使う。

---

## ディレクトリ構成

```text
.
├── apps/
│   ├── api/                  # Flask API
│   └── web/                  # Next.js
├── docs/                     # ドキュメント
├── migrations/               # データベースマイグレーション
├── specs/                    # 仕様書
├── .devcontainer/            # Dev Container 設定
├── compose.yaml              # Docker Compose（ローカル開発）
├── compose.prod.yaml         # Docker Compose（VPS本番、docs/vps-deploy.md）
├── openapi.json              # OpenAPI 定義
├── ONBOARDING.md             # 初回セットアップ
└── CONTRIBUTING.md           # コントリビューションガイド
```

---

## 現在の状況

| コンポーネント | 状態 |
|---------------|------|
| API | 利用可能 |
| PostgreSQL | 利用可能 |
| Dev Container | 利用可能 |
| Docker Compose | 利用可能 |
| フロントエンド | 実装済み（自動起動は未設定） |

### API

API は `apps/api` に配置されています。

Dev Container の起動時に自動で開始されます。

詳細は以下を参照してください。

```
apps/api/README.md
```

### Web

フロントエンドは `apps/web` に配置されています。画面の実装（ログイン・タイムライン・目標・掲示板等）自体は
進んでいますが、`compose.yaml` の `web` サービスは `profiles: [app]` を付けて無効化したままのため、
Dev Container を開いただけでは自動起動しません。恒久的に有効化する手順は `compose.yaml` の
コメントを参照してください。

それまでは `dev` コンテナ内で以下を実行してください。

```bash
cd apps/web
npm run dev
```

起動後、

```
http://localhost:3000
```

へアクセスしてください。

---

## システム構成

```text
Browser
    │
    ▼
Next.js
    │
    ▼
Flask API
    │
    ▼
PostgreSQL
```

各サービスは Docker Compose により管理されます。

---

## 関連ドキュメント

| ファイル | 内容 |
|----------|------|
| ONBOARDING.md | 初回セットアップ |
| apps/api/README.md | API ドキュメント |

上記3文書（規約）以外の参考資料。規約は必ず本README冒頭の表を参照してください。

---

## コントリビューション

Pull Request を作成する前に `CONTRIBUTING.md` をご確認ください。

開発時は以下の内容に従ってください。

- ブランチ運用ルール
- プロジェクトの開発方針
- Pull Request の作成手順
- Spec Kit の運用手順

バグ修正、ドキュメント改善、機能追加など、内容を問わずコントリビューションを歓迎します。

---

## ライセンス

ライセンスについては、プロジェクトで採用するライセンスに従います。
